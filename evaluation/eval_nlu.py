"""Offline evaluation of the language-understanding layer (no API key needed).

    python -m evaluation.eval_nlu

Reads evaluation/nlu_cases.csv and reports accuracy per language. A case passes when the parsed
value equals the expected JSON. ``null`` means "the parser must refuse to guess".
Add your own cases (especially real transcripts that failed) - that is how you improve it.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scheme_saathi.parsing import extract_facts, parse_answer  # noqa: E402


def run(path: Path) -> tuple[dict, list]:
    stats = defaultdict(lambda: [0, 0])
    failures = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            expected = json.loads(row["expected_json"])
            if row["asked_slot"] == "free":
                got = extract_facts(row["utterance"])
            else:
                got = parse_answer(row["asked_slot"], row["utterance"])
            ok = got == expected
            stats[row["language"]][0] += ok
            stats[row["language"]][1] += 1
            if not ok:
                failures.append((row, got))
    return stats, failures


def main() -> int:
    stats, failures = run(ROOT / "evaluation" / "nlu_cases.csv")
    total_ok = sum(a for a, _ in stats.values())
    total = sum(b for _, b in stats.values())
    print("| Language | Passed | Total | Accuracy |\n|---|---|---|---|")
    for lang, (a, b) in sorted(stats.items()):
        print(f"| {lang} | {a} | {b} | {a / b:.0%} |")
    print(f"| **All** | {total_ok} | {total} | {total_ok / total:.0%} |")
    for row, got in failures:
        print(f"\nFAIL [{row['language']}/{row['asked_slot']}] {row['utterance']!r}\n  expected {row['expected_json']}  got {got!r}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
