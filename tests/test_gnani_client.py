import io
import json
import wave

import pytest
import requests

import struct

from scheme_saathi.gnani_client import (GnaniClient, GnaniError, concat_wavs, fix_wav_header, split_text, wav_duration_seconds)


def make_wav(seconds=1.0, rate=16000):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(rate * seconds))
    return buf.getvalue()


class FakeResp:
    def __init__(self, status=200, json_body=None, content=b"", headers=None):
        self.status_code = status
        self._json = json_body
        self.content = content
        self.text = json.dumps(json_body) if json_body is not None else content.decode("latin1", "ignore")
        self.headers = headers or {}

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, **kw):
        self.calls.append((url, kw))
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def client(responses, **kw):
    s = FakeSession(responses)
    return GnaniClient("key", session=s, sleep=lambda _: None, **kw), s


def test_missing_key_raises_config_error():
    with pytest.raises(GnaniError) as e:
        GnaniClient("  ")
    assert e.value.kind == "config"


def test_transcribe_success_sends_correct_request():
    c, s = client([FakeResp(200, {"success": True, "request_id": "r1", "transcript": " नमस्ते "})])
    res = c.transcribe(make_wav(), "hi-IN")
    assert res.transcript == "नमस्ते" and res.request_id == "r1"
    url, kw = s.calls[0]
    assert url == "https://api.vachana.ai/stt/v3"
    assert kw["headers"] == {"X-API-Key-ID": "key"}
    assert kw["data"] == {"language_code": "hi-IN", "format": "transcribe"}
    assert "audio_file" in kw["files"]


def test_transcribe_empty_transcript_is_ok_not_error():
    c, _ = client([FakeResp(200, {"success": True, "transcript": ""})])
    assert c.transcribe(make_wav(), "en-IN").transcript == ""


@pytest.mark.parametrize("audio,kind", [(b"", "audio"), (make_wav(61), "audio"), (make_wav(0.05), "audio")])
def test_transcribe_rejects_bad_audio_before_calling_api(audio, kind):
    c, s = client([])
    with pytest.raises(GnaniError) as e:
        c.transcribe(audio, "en-IN")
    assert e.value.kind == kind and s.calls == []


def test_transcribe_unsupported_language():
    c, _ = client([])
    with pytest.raises(GnaniError):
        c.transcribe(make_wav(), "fr-FR")


def test_retries_on_503_then_succeeds():
    c, s = client([FakeResp(503, {"error": {"message": "down"}}), FakeResp(200, {"success": True, "transcript": "ok"})])
    assert c.transcribe(make_wav(), "en-IN").transcript == "ok" and len(s.calls) == 2


def test_gives_up_after_retries():
    c, s = client([FakeResp(503, {"error": {"message": "down"}})] * 3)
    with pytest.raises(GnaniError) as e:
        c.transcribe(make_wav(), "en-IN")
    assert e.value.kind == "server" and len(s.calls) == 3


def test_network_errors_are_wrapped_and_retried():
    c, s = client([requests.ConnectionError("x"), requests.Timeout("y"), requests.ConnectionError("z")])
    with pytest.raises(GnaniError) as e:
        c.transcribe(make_wav(), "en-IN")
    assert e.value.kind == "network" and len(s.calls) == 3


def test_403_is_auth_error_with_helpful_message_and_no_retry():
    c, s = client([FakeResp(403, {"error": {"type": "FORBIDDEN", "message": "no credits"}})])
    with pytest.raises(GnaniError) as e:
        c.transcribe(make_wav(), "en-IN")
    assert e.value.kind == "auth" and "no credits" in str(e.value) and len(s.calls) == 1


def test_non_json_success_body_is_handled():
    c, _ = client([FakeResp(200, None, b"<html>")])
    with pytest.raises(GnaniError) as e:
        c.transcribe(make_wav(), "en-IN")
    assert e.value.kind == "bad_response"


def test_synthesize_sends_documented_payload_and_returns_wav():
    wav = make_wav()
    c, s = client([FakeResp(200, None, wav, {"Content-Type": "audio/wav"})])
    out = c.synthesize("नमस्ते", "hi-IN")
    assert out == wav
    url, kw = s.calls[0]
    assert url == "https://api.vachana.ai/api/v1/tts/inference"
    p = kw["json"]
    assert p["model"] == "timbre-v2.5" and p["voice"] == "Nalini" and p["language"] == "hi-IN"
    assert p["audio_config"]["container"] == "wav" and p["audio_config"]["encoding"] == "linear_pcm"


def test_synthesize_falls_back_to_v3_when_voice_rejected():
    wav = make_wav()
    c, s = client([FakeResp(400, {"error": {"message": "voice not supported"}}), FakeResp(200, None, wav)])
    assert c.synthesize("hello", "en-IN") == wav
    assert s.calls[1][1]["json"]["model"] == "timbre-v3.0" and s.calls[1][1]["json"]["voice"] == "Shivani"
    assert c.tts_model_in_use == "timbre-v3.0"


def test_synthesize_raises_when_both_models_reject():
    c, _ = client([FakeResp(400, {"error": {"message": "bad"}})] * 2)
    with pytest.raises(GnaniError) as e:
        c.synthesize("hello", "en-IN")
    assert e.value.kind == "bad_request"


def test_synthesize_rejects_json_masquerading_as_audio():
    c, _ = client([FakeResp(200, {"oops": 1}, b'{"oops":1}', {"Content-Type": "application/json"})])
    with pytest.raises(GnaniError) as e:
        c.synthesize("hello", "en-IN")
    assert e.value.kind == "bad_response"


def test_long_text_is_chunked_into_several_calls_and_joined():
    text = ("This is a sentence that is fairly long. " * 20).strip()  # ~800 chars
    n = len(split_text(text))
    assert n >= 3
    c, s = client([FakeResp(200, None, make_wav(0.5)) for _ in range(n)])
    out = c.synthesize(text, "en-IN")
    assert len(s.calls) == n
    assert abs(wav_duration_seconds(out) - 0.5 * n) < 0.01


def test_split_text_handles_devanagari_danda_and_empty():
    assert split_text("") == []
    assert split_text("यह एक वाक्य है। यह दूसरा है।", 20) == ["यह एक वाक्य है।", "यह दूसरा है।"]
    assert all(len(x) <= 10 for x in split_text("a" * 5 + " " + "b" * 5 + " " + "c" * 5, 10))


def test_concat_rejects_mismatched_formats():
    with pytest.raises(GnaniError):
        concat_wavs([make_wav(rate=16000), make_wav(rate=24000)])


def test_kannada_uses_kannada_voice_and_code():
    c, s = client([FakeResp(200, None, make_wav())])
    c.synthesize("ನಮಸ್ಕಾರ", "kn-IN")
    p = s.calls[0][1]["json"]
    assert p["language"] == "kn-IN" and p["voice"] == "Kavin" and p["model"] == "timbre-v2.5"


def test_kannada_stt_language_code_is_sent():
    c, s = client([FakeResp(200, {"success": True, "transcript": "ಹೌದು"})])
    assert c.transcribe(make_wav(), "kn-IN").transcript == "ಹೌದು"
    assert s.calls[0][1]["data"]["language_code"] == "kn-IN"


def streaming_wav(seconds=1.0, rate=24000):
    """A WAV like the one Gnani returned: header sizes are the 0xFFFFFFFF placeholder."""
    pcm = b"\x00\x00" * int(rate * seconds)
    hdr = (b"RIFF" + struct.pack("<I", 0xFFFFFFFF) + b"WAVE" + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16)
           + b"data" + struct.pack("<I", 0xFFFFFFFF))
    return hdr + pcm


def test_streaming_wav_duration_uses_real_bytes_not_header():
    # This is the exact bug seen on a real run: duration came out as 89478 seconds.
    assert wav_duration_seconds(streaming_wav(2.0)) == pytest.approx(2.0)
    assert wav_duration_seconds(make_wav(1.5)) == pytest.approx(1.5)
    assert wav_duration_seconds(b"not a wav") is None
    assert wav_duration_seconds(b"") is None


def test_fix_wav_header_makes_a_standard_wav():
    fixed = fix_wav_header(streaming_wav(1.0))
    with wave.open(io.BytesIO(fixed), "rb") as w:
        assert w.getnframes() == 24000 and w.getframerate() == 24000
    assert fix_wav_header(b"junk") is None


def test_tts_streaming_wav_is_normalised_and_can_go_straight_to_stt():
    c, s = client([FakeResp(200, None, streaming_wav(1.0), {"Content-Type": "audio/wav"}),
                   FakeResp(200, {"success": True, "transcript": "ok"})])
    audio = c.synthesize("hello", "en-IN")
    with wave.open(io.BytesIO(audio), "rb") as w:
        assert w.getnframes() == 24000          # standard header now
    assert c.transcribe(audio, "en-IN").transcript == "ok"  # no 'recording too long' error


def test_streaming_wav_directly_to_stt_is_accepted():
    c, _ = client([FakeResp(200, {"success": True, "transcript": "ok"})])
    assert c.transcribe(streaming_wav(1.0), "en-IN").transcript == "ok"


def test_truncated_odd_byte_count_is_handled():
    assert wav_duration_seconds(streaming_wav(1.0) + b"\x01") == pytest.approx(1.0)
