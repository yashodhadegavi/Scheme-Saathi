"""Smoke-tests the Streamlit UI end to end with Streamlit's AppTest (no real network)."""
import io
import wave
from pathlib import Path
from unittest import mock

import pytest

APP = Path(__file__).resolve().parent.parent / "app.py"
pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest


def _wav():
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(b"\0\0" * 2400)
    return b.getvalue()


@pytest.fixture(autouse=True)
def no_env_key(monkeypatch, tmp_path):
    monkeypatch.delenv("GNANI_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)  # so a developer's real .env in cwd cannot leak into the test
    from scheme_saathi import config
    monkeypatch.setattr(config, "load_env", lambda path=None: None)


def new_app():
    return AppTest.from_file(str(APP), default_timeout=30).run()


def test_loads_without_key_and_shows_notice():
    at = new_app()
    assert not at.exception
    assert any("No Gnani API key" in i.value for i in at.info)
    assert at.title[0].value == "Scheme Saathi"


def test_typed_conversation_reaches_results():
    at = new_app()
    at.sidebar.multiselect[0].set_value(["farm", "pension"]).run()   # the original four schemes
    assert not at.exception
    for ans in ["I am 35 years old and I have 2 acres", "yes", "no", "no", "no", "no"]:
        at.chat_input[0].set_value(ans).run()
        assert not at.exception, at.exception
    assert any("PM-KISAN" in str(m.value) for m in at.markdown)  # result cards rendered
    assert any("guidance" in c.value.lower() or "prototype" in c.value.lower() for c in at.caption)


def test_language_switch_resets_conversation():
    at = new_app()
    at.sidebar.selectbox[0].select("te-IN").run()
    assert not at.exception
    assert at.title[0].value == "స్కీమ్ సాథీ"


def test_kannada_ui_and_conversation():
    at = new_app()
    at.sidebar.selectbox[0].select("kn-IN").run()
    assert not at.exception and at.title[0].value == "ಸ್ಕೀಮ್ ಸಾಥಿ"
    at.chat_input[0].set_value("ಮೂವತ್ತೈದು").run()
    assert not at.exception


def test_with_key_voice_replies_are_requested_and_errors_do_not_crash():
    import scheme_saathi.gnani_client as gc

    class R:
        status_code = 200
        content = _wav()
        headers = {"Content-Type": "audio/wav"}
        text = ""
        def json(self): raise ValueError

    with mock.patch.dict("os.environ", {"GNANI_API_KEY": "k"}), \
         mock.patch.object(gc.requests.Session, "post", return_value=R()) as post:
        at = new_app()
        assert not at.exception
        assert post.called  # greeting was synthesised
        assert any("Gnani API key found" in x.value for x in at.success)
        at.chat_input[0].set_value("35").run()
        assert not at.exception

    class Bad(R):
        status_code = 403
        content = b""
        text = "{}"
        def json(self): return {"error": {"message": "no credits"}}

    with mock.patch.dict("os.environ", {"GNANI_API_KEY": "k"}), \
         mock.patch.object(gc.requests.Session, "post", return_value=Bad()):
        at = new_app()
        assert not at.exception          # app still loads
        assert any("unavailable" in w.value for w in at.warning)


def test_housing_topic_and_note_cards_render():
    at = new_app()
    at.sidebar.multiselect[0].set_value(["housing"]).run()
    for ans in ["yes", "no", "2 lakh"]:
        at.chat_input[0].set_value(ans).run()
        assert not at.exception, at.exception
    text = " ".join(str(m.value) for m in at.markdown)
    assert "PM Awas Yojana, Urban" in text
    assert any("Good to know" in c.value for c in at.caption)


def test_all_topics_default_and_every_language_boots():
    for code, title in (("en-IN", "Scheme Saathi"), ("hi-IN", "स्कीम साथी"), ("te-IN", "స్కీమ్ సాథీ"), ("kn-IN", "ಸ್ಕೀಮ್ ಸಾಥಿ")):
        at = new_app()
        at.sidebar.selectbox[0].select(code).run()
        assert not at.exception and at.title[0].value == title
        assert len(at.sidebar.multiselect[0].value) == 5
