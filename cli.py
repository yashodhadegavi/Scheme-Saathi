"""Terminal version of Scheme Saathi (typed answers, no API key needed).

    python cli.py              # English
    python cli.py --lang te-IN
"""
import argparse

from scheme_saathi.config import LANGUAGES
from scheme_saathi.dialogue import Dialogue


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en-IN", choices=list(LANGUAGES))
    args = ap.parse_args()
    d = Dialogue(args.lang)
    r = d.start()
    print(f"\nSaathi: {r.text}")
    while not r.done:
        try:
            r = d.handle(input("You:    "))
        except (EOFError, KeyboardInterrupt):
            print()
            return
        print(f"\nSaathi: {r.text}")
    for res in r.results:
        print(f"\n[{res.status.upper()}] {res.scheme.name[d.lang]}")
        if res.failed:
            print("   " + " ".join(c.fail[d.lang] for c in res.failed))
        else:
            print("   " + res.scheme.benefit[d.lang])


if __name__ == "__main__":
    main()
