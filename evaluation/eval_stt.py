"""Measure Prisma STT on YOUR recordings (needs GNANI_API_KEY).

    python -m evaluation.eval_stt --manifest evaluation/manifest.csv

manifest.csv columns:
    audio_path       path to a clip (wav/mp3/ogg/flac/m4a/aac, <= 60 s; keep it ~5 s)
    language         en-IN | hi-IN | te-IN
    speaker          any label (e.g. "amma", "friend1") - lets you see per-speaker differences
    condition        e.g. quiet / noisy / phone
    reference_text   what was actually said (used for word error rate)
    asked_slot       the question the clip answers (age, has_bank_account, ...)
    expected_json    the fact you expect, e.g. 35 or true or false or "unsure"

Writes evaluation/results/stt_report.md with WER, key-fact accuracy and latency, plus every
failure so you can see *why* it failed and fix it. See evaluation/RECORDING_GUIDE.md.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scheme_saathi import config  # noqa: E402
from scheme_saathi.gnani_client import GnaniClient, GnaniError  # noqa: E402
from scheme_saathi.metrics import percentile, wer  # noqa: E402
from scheme_saathi.parsing import parse_answer  # noqa: E402


def evaluate(client: GnaniClient, manifest: Path, delay: float = 0.3) -> list[dict]:
    results = []
    base = manifest.parent
    with manifest.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            path = Path(row["audio_path"])
            path = path if path.is_absolute() else (base / path if (base / path).exists() else ROOT / path)
            rec = dict(row, transcript="", error="", latency=None, wer=None, fact_ok=None, parsed=None)
            try:
                res = client.transcribe(path.read_bytes(), row["language"], filename=path.name)
                rec.update(transcript=res.transcript, latency=res.latency_s)
                if row.get("reference_text"):
                    rec["wer"] = wer(row["reference_text"], res.transcript)
                if row.get("asked_slot") and row.get("expected_json"):
                    parsed = parse_answer(row["asked_slot"], res.transcript)
                    rec["parsed"] = parsed
                    rec["fact_ok"] = parsed == json.loads(row["expected_json"])
            except (GnaniError, OSError) as e:
                rec["error"] = str(e)
            results.append(rec)
            time.sleep(delay)
    return results


def report(results: list[dict]) -> str:
    by_lang: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by_lang[r["language"]].append(r)
    lines = ["# STT evaluation report", "", f"Clips: {len(results)}", "",
             "| Language | Clips | Errors | Mean WER | Key-fact accuracy | p50 latency | p95 latency |",
             "|---|---|---|---|---|---|---|"]
    for lang, rs in sorted(by_lang.items()):
        ok = [r for r in rs if not r["error"]]
        wers = [r["wer"] for r in ok if r["wer"] is not None]
        facts = [r["fact_ok"] for r in ok if r["fact_ok"] is not None]
        lats = [r["latency"] for r in ok if r["latency"] is not None]
        lines.append(
            f"| {lang} | {len(rs)} | {len(rs) - len(ok)} | "
            f"{(sum(wers) / len(wers)) if wers else float('nan'):.2f} | "
            f"{(sum(facts) / len(facts)) if facts else float('nan'):.0%} | "
            f"{percentile(lats, 50):.2f}s | {percentile(lats, 95):.2f}s |")
    bad = [r for r in results if r["error"] or r["fact_ok"] is False]
    lines += ["", "## Failures (read these - they are where the learning is)", ""]
    if not bad:
        lines.append("None.")
    for r in bad:
        lines.append(f"- `{r['audio_path']}` [{r['language']}, {r.get('speaker','')}, {r.get('condition','')}] "
                     f"said: {r.get('reference_text','')!r} -> heard: {r['transcript']!r} "
                     f"(parsed {r['parsed']!r}, expected {r.get('expected_json')}) {r['error']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(ROOT / "evaluation" / "manifest.csv"))
    ap.add_argument("--out", default=str(ROOT / "evaluation" / "results" / "stt_report.md"))
    ap.add_argument("--delay", type=float, default=0.3, help="seconds between calls (rate limits)")
    args = ap.parse_args()
    key = config.get_api_key()
    if not key:
        print("Set GNANI_API_KEY (in .env or the environment) first.")
        return 2
    manifest = Path(args.manifest)
    if not manifest.exists():
        print(f"{manifest} not found. Copy evaluation/manifest_template.csv to evaluation/manifest.csv and fill it in.")
        return 2
    results = evaluate(GnaniClient(key), manifest, args.delay)
    text = report(results)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
