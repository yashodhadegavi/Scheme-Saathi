# How to build your evaluation set (this is the part reviewers remember)

Goal: **30-40 short clips from at least 5 different speakers**, in the languages you demo.

1. Pick the questions the app really asks (see `scheme_saathi/i18n.py`): age and the yes/no ones.
2. For each speaker record 6-8 answers, ~3-5 seconds each, as `.wav` (phone voice recorder is fine).
   Mix: quiet room, noisy room (fan, street, TV), and one older speaker if you can.
   Include natural variety: "haan", "avunu", "hmm yes I have", a mixed-language answer.
3. Save clips in `evaluation/audio/` and list them in `evaluation/manifest.csv`
   (copy `manifest_template.csv`). `reference_text` = what was really said.
4. Run: `python -m evaluation.eval_stt`
5. Open `evaluation/results/stt_report.md`. For each failure ask: bad audio? accent? a word the
   parser does not know? Fix the cause (add the word to `scheme_saathi/lexicon.py`, add a case to
   `evaluation/nlu_cases.csv`), re-run, and write the before/after in your write-up.

Tip: also run `python -m scripts.smoke_test_api --save-dir evaluation/audio_synthetic` to
produce *synthetic* clips from Gnani's TTS. They are useful to check the pipeline, but do NOT
report them as accuracy - synthetic voices are much cleaner than real people.

Be honest in the write-up about sample size. "31/38 clips, 5 speakers" is a strong, credible
sentence; "99% accurate" from 10 clips is not.
