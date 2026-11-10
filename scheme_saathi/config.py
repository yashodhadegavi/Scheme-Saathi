"""Central configuration: endpoints, languages, voices, and environment loading."""
from __future__ import annotations

import os
from pathlib import Path

# --- Gnani Vachana endpoints (see https://docs.gnani.ai) -------------------------------------
STT_URL = "https://api.vachana.ai/stt/v3"
TTS_URL = "https://api.vachana.ai/api/v1/tts/inference"

# --- Languages supported by this app (all also supported by Prisma STT and Timbre TTS) -----
LANGUAGES = {
    "en-IN": "English",
    "hi-IN": "हिन्दी (Hindi)",
    "te-IN": "తెలుగు (Telugu)",
    "kn-IN": "ಕನ್ನಡ (Kannada)",
}
SHORT = {"en-IN": "en", "hi-IN": "hi", "te-IN": "te", "kn-IN": "kn"}

# --- TTS defaults ----------------------------------------------------------------------------
# Timbre v2.5 voices have one preferred language each; v3.0 voices speak all 10 languages.
# Voice names come from https://docs.gnani.ai/api/TTS/available-voices.md
DEFAULT_TTS_MODEL = "timbre-v2.5"
V25_VOICES = {"en-IN": "Kaveri", "hi-IN": "Nalini", "te-IN": "Suhana", "kn-IN": "Kavin"}
V30_VOICE = "Shivani"
FALLBACK_TTS_MODEL = "timbre-v3.0"

# --- Limits (from the STT REST docs: max 60 s, ideal <= 30 s) ----------------------------------
MAX_AUDIO_SECONDS = 60
MAX_AUDIO_BYTES = 10 * 1024 * 1024
TTS_CHUNK_CHARS = 300  # long replies are split at sentence ends and the WAVs joined

DATA_DIR = Path(__file__).parent / "data"
SCHEMES_FILE = DATA_DIR / "schemes.json"


def load_env(path: str | os.PathLike | None = None) -> None:
    """Tiny .env loader (no dependency). Existing environment variables win."""
    candidates = [Path(path)] if path else [Path.cwd() / ".env", Path(__file__).parent.parent / ".env"]
    for p in candidates:
        if not p.is_file():
            continue
        for raw in p.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val
        break


def get_api_key() -> str:
    load_env()
    return os.environ.get("GNANI_API_KEY", "").strip()


def default_voice(model: str, language_code: str) -> str:
    if model == "timbre-v3.0":
        return V30_VOICE
    return V25_VOICES.get(language_code, "Kaveri")


# Used by the sidebar "Test Gnani connection" button: speak with Timbre, read back with Prisma.
SELF_TEST_PHRASES = {
    "en-IN": "I am thirty five years old",
    "hi-IN": "मेरी उम्र पैंतीस साल है",
    "te-IN": "నా వయసు ముప్పై ఐదు సంవత్సరాలు",
    "kn-IN": "ನನ್ನ ವಯಸ್ಸು ಮೂವತ್ತೈದು ವರ್ಷ",
}
