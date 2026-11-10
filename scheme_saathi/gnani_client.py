"""Thin, defensive client for Gnani's Vachana REST APIs.

STT  : POST https://api.vachana.ai/stt/v3                (multipart; header X-API-Key-ID)
TTS  : POST https://api.vachana.ai/api/v1/tts/inference  (JSON; returns binary audio)

Endpoints, field names and limits follow https://docs.gnani.ai (checked 2026-10-24).
We call the REST endpoints directly with ``requests`` instead of the optional SDK so the
project has one small dependency and every failure mode is visible and handled here.
"""
from __future__ import annotations

import io
import re
import struct
import time
import wave
from dataclasses import dataclass
from typing import Callable

import requests

from . import config


class GnaniError(Exception):
    """Raised for every failure talking to Gnani. ``kind`` lets the UI choose a friendly message."""

    def __init__(self, message: str, status: int | None = None, kind: str = "error"):
        super().__init__(message)
        self.status = status
        self.kind = kind  # config | audio | auth | bad_request | rate_limit | server | network | bad_response


@dataclass
class STTResult:
    transcript: str
    request_id: str | None
    latency_s: float


# --------------------------------------------------------------------------------------------
# Audio helpers (pure functions, unit-tested)
# --------------------------------------------------------------------------------------------
def _parse_wav(data: bytes) -> tuple[int, int, int, bytes] | None:
    """Read a PCM WAV and return (channels, sample_width_bytes, sample_rate, pcm_bytes).

    Gnani's TTS can return a *streaming* WAV whose header declares a placeholder length
    (0xFFFFFFFF). We therefore never trust the declared sizes: the audio length is whatever
    bytes are really present. Returns None if this is not a PCM WAV we understand.
    """
    if len(data) < 44 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return None
    fmt = None
    pos = 12
    while pos + 8 <= len(data):
        chunk_id = data[pos:pos + 4]
        declared = struct.unpack("<I", data[pos + 4:pos + 8])[0]
        body = pos + 8
        if chunk_id == b"fmt " and body + 16 <= len(data):
            audio_format, channels, rate, _byte_rate, _align, bits = struct.unpack("<HHIIHH", data[body:body + 16])
            if audio_format not in (1, 0xFFFE) or channels < 1 or rate < 1 or bits % 8 or bits < 8:
                return None
            fmt = (channels, bits // 8, rate)
        elif chunk_id == b"data":
            if fmt is None:
                return None
            available = len(data) - body
            length = available if declared in (0, 0xFFFFFFFF) or declared > available else declared
            frame = fmt[0] * fmt[1]
            length -= length % frame  # whole frames only
            return fmt[0], fmt[1], fmt[2], data[body:body + length]
        if declared > len(data) - body:  # bogus chunk size: stop looking
            return None
        pos = body + declared + (declared & 1)
    return None


def wav_duration_seconds(data: bytes) -> float | None:
    """Real duration of a WAV in seconds (from the bytes present), or None if unreadable."""
    parsed = _parse_wav(data)
    if parsed is None:
        return None
    channels, width, rate, pcm = parsed
    return len(pcm) / float(channels * width * rate)


def fix_wav_header(data: bytes) -> bytes | None:
    """Rewrite a WAV with a correct header (fixes streaming WAVs). None if unreadable."""
    parsed = _parse_wav(data)
    if parsed is None:
        return None
    channels, width, rate, pcm = parsed
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(width)
        w.setframerate(rate)
        w.writeframes(pcm)
    return out.getvalue()


def concat_wavs(parts: list[bytes]) -> bytes:
    """Join WAV files that share the same format into one WAV."""
    if not parts:
        raise GnaniError("No audio to join", kind="bad_response")
    if len(parts) == 1:
        return parts[0]
    out = io.BytesIO()
    params = None
    with wave.open(out, "wb") as dst:
        for p in parts:
            try:
                with wave.open(io.BytesIO(p), "rb") as src:
                    cur = (src.getnchannels(), src.getsampwidth(), src.getframerate())
                    if params is None:
                        params = cur
                        dst.setnchannels(cur[0])
                        dst.setsampwidth(cur[1])
                        dst.setframerate(cur[2])
                    elif cur != params:
                        raise GnaniError("Audio chunks have different formats", kind="bad_response")
                    dst.writeframes(src.readframes(src.getnframes()))
            except (wave.Error, EOFError) as e:
                raise GnaniError(f"Could not read audio chunk: {e}", kind="bad_response") from e
    return out.getvalue()


_SENTENCE_END = re.compile(r"(?<=[.!?।])\s+")


def split_text(text: str, max_chars: int = config.TTS_CHUNK_CHARS) -> list[str]:
    """Split text at sentence ends into chunks of at most ``max_chars`` characters."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if not text:
        return []
    chunks: list[str] = []
    cur = ""
    for sent in _SENTENCE_END.split(text):
        while len(sent) > max_chars:  # a single very long sentence: cut at the last space
            cut = sent.rfind(" ", 0, max_chars)
            cut = cut if cut > 0 else max_chars
            piece, sent = sent[:cut].strip(), sent[cut:].strip()
            if cur:
                chunks.append(cur)
                cur = ""
            chunks.append(piece)
        if not sent:
            continue
        if cur and len(cur) + 1 + len(sent) > max_chars:
            chunks.append(cur)
            cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    if cur:
        chunks.append(cur)
    return chunks


_MIME = {
    "wav": "audio/wav", "mp3": "audio/mpeg", "ogg": "audio/ogg", "flac": "audio/flac",
    "aac": "audio/aac", "m4a": "audio/mp4",
}


def _mime_for(filename: str) -> str:
    return _MIME.get(filename.rsplit(".", 1)[-1].lower(), "application/octet-stream")


# --------------------------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------------------------
class GnaniClient:
    RETRY_STATUS = {429, 500, 502, 503, 504}

    def __init__(
        self,
        api_key: str,
        *,
        session: requests.Session | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        backoff: float = 1.0,
        sleep: Callable[[float], None] = time.sleep,
    ):
        if not api_key or not api_key.strip():
            raise GnaniError("GNANI_API_KEY is missing", kind="config")
        self.api_key = api_key.strip()
        self.session = session or requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff
        self._sleep = sleep
        self.tts_model_in_use: str | None = None  # remembers which model worked

    # ----------------------------------------------------------------------------------------
    def _headers(self) -> dict[str, str]:
        return {"X-API-Key-ID": self.api_key}

    @staticmethod
    def _error_message(resp: requests.Response) -> str:
        try:
            body = resp.json()
            err = body.get("error") if isinstance(body, dict) else None
            if isinstance(err, dict) and err.get("message"):
                return str(err["message"])
            if isinstance(body, dict) and body.get("detail"):
                return str(body["detail"])
        except ValueError:
            pass
        return (resp.text or "").strip()[:200] or f"HTTP {resp.status_code}"

    def _post(self, url: str, **kwargs) -> requests.Response:
        """POST with retry/backoff on transient errors; raises GnaniError on any failure."""
        last: GnaniError | None = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.session.post(url, headers=self._headers(), timeout=self.timeout, **kwargs)
            except (requests.ConnectionError, requests.Timeout) as e:
                last = GnaniError(f"Network problem talking to Gnani: {e.__class__.__name__}", kind="network")
            else:
                if resp.status_code < 400:
                    return resp
                msg = self._error_message(resp)
                if resp.status_code in (401, 403):
                    raise GnaniError(
                        f"Gnani rejected the request ({resp.status_code}): {msg}. "
                        "Check your API key and remaining credits.", resp.status_code, "auth")
                if resp.status_code == 400:
                    raise GnaniError(f"Bad request: {msg}", 400, "bad_request")
                kind = "rate_limit" if resp.status_code == 429 else "server"
                last = GnaniError(f"Gnani error {resp.status_code}: {msg}", resp.status_code, kind)
                if resp.status_code not in self.RETRY_STATUS:
                    raise last
            if attempt < self.max_retries:
                self._sleep(self.backoff * (2 ** attempt))
        assert last is not None
        raise last

    # ----------------------------------------------------------------------------------------
    # Speech to text (Prisma)
    # ----------------------------------------------------------------------------------------
    def transcribe(
        self, audio: bytes, language_code: str = "en-IN", filename: str = "audio.wav", itn: bool = True
    ) -> STTResult:
        if language_code not in config.LANGUAGES:
            raise GnaniError(f"Unsupported language: {language_code}", kind="config")
        if not audio:
            raise GnaniError("No audio was recorded", kind="audio")
        if len(audio) > config.MAX_AUDIO_BYTES:
            raise GnaniError("Audio file is too large", kind="audio")
        dur = wav_duration_seconds(audio)
        if dur is not None:
            if dur > config.MAX_AUDIO_SECONDS:
                raise GnaniError(
                    f"Recording is {dur:.0f}s; the limit is {config.MAX_AUDIO_SECONDS}s. Please keep answers short.",
                    kind="audio")
            if dur < 0.2:
                raise GnaniError("Recording is too short", kind="audio")

        t0 = time.perf_counter()
        resp = self._post(
            config.STT_URL,
            files={"audio_file": (filename, audio, _mime_for(filename))},
            data={"language_code": language_code, "format": "transcribe" if itn else "verbatim"},
        )
        latency = time.perf_counter() - t0
        try:
            body = resp.json()
        except ValueError as e:
            raise GnaniError("Gnani returned a response that is not JSON", kind="bad_response") from e
        if not isinstance(body, dict) or body.get("success") is False:
            raise GnaniError(f"Transcription failed: {body}", kind="bad_response")
        return STTResult(str(body.get("transcript") or "").strip(), body.get("request_id"), latency)

    # ----------------------------------------------------------------------------------------
    # Text to speech (Timbre)
    # ----------------------------------------------------------------------------------------
    def _tts_attempts(self, language_code: str, model: str | None, voice: str | None) -> list[tuple[str, str]]:
        primary_model = model or self.tts_model_in_use or config.DEFAULT_TTS_MODEL
        primary = (primary_model, voice or config.default_voice(primary_model, language_code))
        other_model = config.FALLBACK_TTS_MODEL if primary_model != config.FALLBACK_TTS_MODEL else config.DEFAULT_TTS_MODEL
        return [primary, (other_model, config.default_voice(other_model, language_code))]

    def _synth_one(self, text: str, language_code: str, model: str, voice: str, speed: float) -> bytes:
        payload = {
            "text": text,
            "voice": voice,
            "model": model,
            "language": language_code,
            "speed": speed,
            "audio_config": {
                "sample_rate": 24000, "num_channels": 1, "sample_width": 2,
                "encoding": "linear_pcm", "container": "wav",
            },
        }
        resp = self._post(config.TTS_URL, json=payload)
        data = resp.content
        if "json" in (resp.headers.get("Content-Type") or "").lower() or not data.startswith(b"RIFF"):
            raise GnaniError("TTS did not return a WAV file", kind="bad_response")
        return fix_wav_header(data) or data  # normalise streaming-style headers

    def synthesize(
        self, text: str, language_code: str = "en-IN", *, voice: str | None = None,
        model: str | None = None, speed: float = 1.0,
    ) -> bytes:
        """Return WAV bytes. Long text is chunked at sentence ends; a rejected model/voice falls
        back once to the other Timbre model so a catalogue mismatch never blocks the demo."""
        if language_code not in config.LANGUAGES:
            raise GnaniError(f"Unsupported language: {language_code}", kind="config")
        chunks = split_text(text)
        if not chunks:
            raise GnaniError("Nothing to speak", kind="config")
        wavs = []
        for chunk in chunks:
            wavs.append(self._synth_with_fallback(chunk, language_code, model, voice, speed))
        return concat_wavs(wavs)

    def _synth_with_fallback(self, chunk, language_code, model, voice, speed) -> bytes:
        last: GnaniError | None = None
        for m, v in self._tts_attempts(language_code, model, voice):
            try:
                audio = self._synth_one(chunk, language_code, m, v, speed)
                self.tts_model_in_use = m
                return audio
            except GnaniError as e:
                if e.kind != "bad_request":
                    raise
                last = e
        assert last is not None
        raise last
