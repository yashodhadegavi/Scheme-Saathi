import csv
import io
import wave
from pathlib import Path

import pytest

from evaluation import eval_nlu, eval_stt
from scheme_saathi.gnani_client import GnaniClient, GnaniError
from scheme_saathi.metrics import edit_distance, percentile, wer

ROOT = Path(__file__).resolve().parent.parent


def test_wer_basics():
    assert wer("a b c", "a b c") == 0
    assert wer("a b c", "a x c") == pytest.approx(1 / 3)
    assert wer("a b", "") == 1
    assert wer("", "") == 0
    assert wer("हाँ नहीं", "हां नहीं") == 0  # normalisation folds chandrabindu into anusvara
    assert edit_distance(list("kitten"), list("sitting")) == 3


def test_percentile():
    assert percentile([1, 2, 3, 4], 50) == 2.5
    assert percentile([5], 95) == 5


def test_nlu_regression_cases_all_pass():
    stats, failures = eval_nlu.run(ROOT / "evaluation" / "nlu_cases.csv")
    assert not failures, failures
    assert sum(b for _, b in stats.values()) >= 40


class _Sess:
    def __init__(self, transcript):
        self.t = transcript

    def post(self, url, **kw):
        class R:
            status_code = 200
            headers = {}
            text = ""
            def json(s): return {"success": True, "request_id": "r", "transcript": self.t}
        return R()


def _wav(path):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b"\0\0" * 8000)


def test_eval_stt_pipeline_with_fake_api(tmp_path):
    _wav(tmp_path / "a.wav"); _wav(tmp_path / "b.wav")
    man = tmp_path / "m.csv"
    with man.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["audio_path", "language", "speaker", "condition", "reference_text", "asked_slot", "expected_json"])
        w.writerow(["a.wav", "en-IN", "me", "quiet", "thirty five", "age", "35"])
        w.writerow(["b.wav", "en-IN", "me", "noisy", "yes", "has_bank_account", "false"])  # deliberately wrong
        w.writerow(["missing.wav", "en-IN", "me", "quiet", "x", "age", "1"])
    client = GnaniClient("k", session=_Sess("thirty five"), sleep=lambda _: None)
    res = eval_stt.evaluate(client, man, delay=0)
    assert res[0]["fact_ok"] is True and res[0]["wer"] == 0
    assert res[1]["fact_ok"] is False
    assert res[2]["error"]
    text = eval_stt.report(res)
    assert "Failures" in text and "missing.wav" in text
