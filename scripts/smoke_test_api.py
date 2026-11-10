"""Check that your API key, network and the Gnani endpoints work - before you record a demo.

    python -m scripts.smoke_test_api
    python -m scripts.smoke_test_api --save-dir evaluation/audio_synthetic

For each language it (1) synthesises a sentence with Timbre TTS, (2) transcribes that audio
with Prisma STT, and (3) checks the age is read back correctly. This proves the plumbing, not
real-world accuracy (the audio is synthetic).
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scheme_saathi import config  # noqa: E402
from scheme_saathi.gnani_client import GnaniClient, GnaniError  # noqa: E402
from scheme_saathi.metrics import wer  # noqa: E402
from scheme_saathi.parsing import parse_age, parse_answer  # noqa: E402

PHRASES = {
    "en-IN": [("I am thirty five years old", "age", 35), ("yes I have a bank account", "has_bank_account", True),
              ("our family income is two lakh rupees a year", "annual_income", 200000)],
    "hi-IN": [("मेरी उम्र पैंतीस साल है", "age", 35), ("हाँ मेरा बैंक खाता है", "has_bank_account", True),
              ("हमारे परिवार की सालाना आय दो लाख रुपये है", "annual_income", 200000)],
    "te-IN": [("నా వయసు ముప్పై ఐదు సంవత్సరాలు", "age", 35), ("అవును నాకు బ్యాంకు ఖాతా ఉంది", "has_bank_account", True),
              ("మా కుటుంబ ఆదాయం ఏడాదికి రెండు లక్షల రూపాయలు", "annual_income", 200000)],
    "kn-IN": [("ನನ್ನ ವಯಸ್ಸು ಮೂವತ್ತೈದು ವರ್ಷ", "age", 35), ("ಹೌದು ನನಗೆ ಬ್ಯಾಂಕ್ ಖಾತೆ ಇದೆ", "has_bank_account", True),
              ("ನಮ್ಮ ಕುಟುಂಬದ ಆದಾಯ ವರ್ಷಕ್ಕೆ ಎರಡು ಲಕ್ಷ ರೂಪಾಯಿ", "annual_income", 200000)],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save-dir", help="save the synthetic clips and a manifest here")
    args = ap.parse_args()

    key = config.get_api_key()
    if not key:
        print("FAIL  GNANI_API_KEY is not set. Copy .env.example to .env and add your key.")
        return 2
    client = GnaniClient(key)
    rows, failures = [], 0
    save = Path(args.save_dir) if args.save_dir else None
    if save:
        save.mkdir(parents=True, exist_ok=True)

    for lang, items in PHRASES.items():
        for i, (phrase, slot, expected) in enumerate(items, 1):
            label = f"{lang} #{i}"
            try:
                wav = client.synthesize(phrase, lang)
                res = client.transcribe(wav, lang)
            except GnaniError as e:
                print(f"FAIL  {label}: {e}")
                failures += 1
                continue
            got = parse_age(res.transcript) if slot == "age" else parse_answer(slot, res.transcript)
            ok = got == expected
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'}  {label}: said {phrase!r} -> heard {res.transcript!r} "
                  f"(WER {wer(phrase, res.transcript):.2f}, STT {res.latency_s:.1f}s, voice model {client.tts_model_in_use})")
            if save:
                name = f"{lang[:2]}_{slot}_{i:02d}.wav"
                (save / name).write_bytes(wav)
                rows.append([f"{save.name}/{name}", lang, "synthetic", "clean", phrase, slot,
                             str(expected).lower() if isinstance(expected, bool) else expected])
    if save and rows:
        with (save / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["audio_path", "language", "speaker", "condition", "reference_text", "asked_slot", "expected_json"])
            w.writerows(rows)
        print(f"Saved {len(rows)} clips + manifest to {save}")
    print("\nAll good." if not failures else f"\n{failures} check(s) failed. See messages above.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
