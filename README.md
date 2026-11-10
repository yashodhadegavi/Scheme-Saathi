# Scheme Saathi

A voice assistant that tells people which Indian government schemes they may qualify for,
in **Kannada, Telugu, Hindi or English** (including mixed speech). Built for the Gnani.ai Great Indian AI
Internship Challenge.

**Where Gnani's models and your API key are used**
- Your key lives in `.env` as `GNANI_API_KEY` and is sent as the `X-API-Key-ID` header on every call
  (`scheme_saathi/gnani_client.py`). Voice only works with a key; typing works without one.
- In the app, the sidebar shows "Gnani API key found" and a **Test Gnani connection** button that
  speaks a sentence with Timbre and reads it back with Prisma in the chosen language.
- The footer of the app credits Gnani Prisma and Timbre. Name both models in your write-up.

**Gnani models used**
- **Prisma (Vachana STT, `POST /stt/v3`)** turns the person's spoken answer into text. We request
  `format=transcribe` so spoken numbers arrive as digits.
- **Timbre (TTS, `POST /api/v1/tts/inference`)** speaks every question and result in the same
  language (Kannada voice: Kavin; Telugu: Suhana; Hindi: Nalini; English: Kaveri). Timbre v2.5 is the default, with an automatic fallback to v3.0 if a voice is rejected.

**How it works**

    mic -> Prisma STT -> parser -> rule engine (plain code) -> dialogue -> Timbre TTS -> speaker

Eligibility is decided by **plain code reading verified rules** (`scheme_saathi/data/schemes.json`),
never by a language model, so answers are reproducible and cannot be invented. The assistant asks
one short question at a time, skips questions that no longer matter, and says "please confirm
locally" instead of guessing when the person is unsure.

Schemes covered (rules checked 24-26 Oct 2026 against the sources listed in `schemes.json`),
grouped into five topics you can pick in the sidebar:

| Topic | Schemes |
|---|---|
| Farmers' income support | PM-KISAN |
| Pension and insurance | Atal Pension Yojana, PM Jeevan Jyoti Bima Yojana, PM Suraksha Bima Yojana |
| Housing | PM Awas Yojana Urban, PM Awas Yojana Gramin |
| Health cover | Ayushman Vay Vandana (age 70+), Ayushman Bharat PM-JAY (family list) |
| Scholarships | National Means cum Merit Scholarship (class 8), Post Matric Scholarship for SC students |

Choosing only the topics you need keeps the conversation short: the assistant asks about 3 to 15
questions depending on the topics and your answers, skipping any that no longer matter.

## Quick start (5 minutes)

Requires Python 3.10+.

    python -m venv .venv
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env               # then paste your key (get it at https://app.gnani.ai/voice)
    python -m scripts.smoke_test_api   # checks key + network + STT + TTS (do this first)
    streamlit run app.py

Without a key the app still runs: typing works, voice is switched off. `python cli.py` gives a
terminal version.

## Using it
1. Choose a language in the sidebar (English, हिन्दी, తెలుగు, ಕನ್ನಡ).
2. Press the mic and answer, or type. A first sentence like "I am 35 and I have 2 acres" lets
   it skip questions.
3. Results appear as cards: benefit, documents to carry, how to apply, official link.
4. "Fix a wrong answer" corrects a mis-heard fact and re-checks instantly.

## Tests and evaluation

    pip install -r requirements-dev.txt
    pytest                              # 141 offline tests: parsing, rules, dialogue, API client, UI
    python -m evaluation.eval_nlu       # language-understanding regression cases
    python -m evaluation.eval_stt       # YOUR recordings vs Prisma: WER, fact accuracy, latency

The 78 NLU cases were written together with the parser, so 100% there is a *regression check*,
not a measure of real-world accuracy. Real accuracy comes from `evaluation.eval_stt` on recordings
of real speakers: follow `evaluation/RECORDING_GUIDE.md` and put those numbers in your write-up.

## Project layout

    app.py                     Streamlit UI
    cli.py                     terminal version
    scheme_saathi/
      gnani_client.py          STT + TTS client: retries, validation, voice fallback, chunking
      parsing.py, lexicon.py   yes/no, age and fact extraction in en/hi/te (+ romanised)
      engine.py                three-valued rule engine, picks the next useful question
      dialogue.py              conversation manager (retries, unsure, corrections)
      i18n.py                  all text in en/hi/te (numbers written as words for clean TTS)
      data/schemes.json        scheme rules, benefits, documents, sources
    evaluation/, scripts/, tests/

## How certain is each result? (be honest about this in your demo)
- **Rule-based and checkable:** PM-KISAN, Atal Pension, the two insurance schemes, PMAY Urban,
  Ayushman Vay Vandana (age 70+).
- **First check only:** PMAY Gramin and Ayushman Bharat PM-JAY (family list) are decided from
  government survey lists (Awaas Plus, SECC). The app screens the visible conditions and tells the
  person to confirm on the list.
- **Changing rules:** scholarship limits differ by state and year. The Post Matric (SC) income limit
  is two and a half lakh now, and the government has said it plans four and a half lakh; edit
  `max` in `schemes.json` when that is confirmed. NMMS dates and exam rules are set by each state.
- Other scholarships (ST, OBC, minority, girls in technical courses) and state health schemes
  (Arogyasri and others) are not included. Add them by editing `schemes.json` and `i18n_extra.py`.

## Known limits (say these out loud in your demo - it builds trust)
- Ten schemes, four languages (English, Hindi, Telugu, Kannada). More are added by editing `schemes.json` and `i18n.py`.
- Understanding is rule-based: unusual phrasing leads to a re-ask, and after repeated misses the
  fact is marked "not sure". It never guesses.
- Real eligibility has extra conditions (for example PM-KISAN land-record and e-KYC checks, state
  rules). The app gives guidance only.
- Hindi, Telugu and Kannada wording was written for this prototype; have native speakers review it (Kannada number words such as ಮೂವತ್ತೈದು especially).
- **Re-verify scheme rules and document lists before any public demo.** Rules change.
- Voice names, models and quotas depend on your Gnani account. If TTS returns 400, pick another
  voice under Advanced in the sidebar.

## Troubleshooting
| Symptom | Fix |
|---|---|
| "Gnani rejected the request" | wrong key, or no credits left |
| Mic widget missing | needs a key; typing always works. Allow mic permission in the browser |
| No sound | browsers block autoplay until you click once; use the play button |
| STT returns empty text | speak closer, keep under 60 s, check the language selected matches |
