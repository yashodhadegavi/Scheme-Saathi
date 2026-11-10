"""Scheme Saathi - Streamlit app.

Run:  streamlit run app.py
"""
from __future__ import annotations

import hashlib
import time

import streamlit as st

from scheme_saathi import config, i18n
from scheme_saathi.dialogue import Dialogue, Reply
from scheme_saathi.engine import CHECK, ELIGIBLE, NOT_ELIGIBLE, SLOT_ORDER, TOPICS, UNSURE, SchemeResult
from scheme_saathi.gnani_client import GnaniClient, GnaniError

st.set_page_config(page_title="Scheme Saathi", page_icon="🌾", layout="centered")

# Noto fonts make Telugu and Devanagari render well on machines that lack them.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600&family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Sans+Kannada:wght@400;600&family=Noto+Sans:wght@400;600&display=swap');
    /* Apply Noto only to text elements. Never to <span>: Streamlit draws its icons (expander
       arrows etc.) with an icon font on spans, and overriding it prints "arrow_right" as text. */
    .stApp, .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp input, .stApp textarea, .stApp button, .stApp [data-testid="stCaptionContainer"] {
        font-family: 'Noto Sans','Noto Sans Telugu','Noto Sans Devanagari','Noto Sans Kannada',sans-serif;
    }
    [data-testid="stIconMaterial"], span[class*="material-symbols"], span[class*="material-icons"] {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    }
    .ss-status { display:inline-block; padding:2px 10px; border-radius:999px; font-size:0.85rem; font-weight:600; }
    .ss-ok   { background:#D6EFE6; color:#0B5A49; }
    .ss-no   { background:#EDE3E1; color:#7A3B2E; }
    .ss-chk  { background:#F7E8C9; color:#7A5410; }
    </style>
    """,
    unsafe_allow_html=True,
)

# slot -> (min, max, default, step) for the "fix a wrong answer" form
NUMERIC_RANGES = {
    "age": (1, 110, 30, 1),
    "annual_income": (1, 100_000_000, 250_000, 10_000),
    "marks_percent": (1, 100, 60, 1),
}

ERROR_HINTS = {
    "auth": "Gnani rejected the request. Check the API key and your remaining credits.",
    "rate_limit": "Too many requests right now. Wait a few seconds and try again.",
    "server": "Gnani's service is having a problem. Try again, or type your answer.",
    "network": "Could not reach Gnani. Check the internet connection, or type your answer.",
    "audio": "",  # message from the client is already user-friendly
    "bad_request": "Gnani could not process this request.",
    "bad_response": "Gnani sent a response the app could not read.",
    "config": "",
}


# ------------------------------------------------------------------------------------------
# State
# ------------------------------------------------------------------------------------------
def init_state() -> None:
    ss = st.session_state
    ss.setdefault("chat", [])            # [{role, text, audio, noted}]
    ss.setdefault("dialogue", None)
    ss.setdefault("mic_n", 0)
    ss.setdefault("form_n", 0)
    ss.setdefault("last_audio_hash", None)
    ss.setdefault("autoplay_idx", None)
    ss.setdefault("tts_cache", {})
    ss.setdefault("stt_latency", None)
    ss.setdefault("tts_latency", None)
    ss.setdefault("notice", None)


def get_client(api_key: str) -> GnaniClient | None:
    if not api_key:
        return None
    ss = st.session_state
    if ss.get("_client_key") != api_key:
        ss["_client"] = GnaniClient(api_key)
        ss["_client_key"] = api_key
    return ss["_client"]


def notify(message: str, level: str = "warning") -> None:
    st.session_state["notice"] = (level, message)


def run_connection_test(client: GnaniClient | None, lang_code: str) -> None:
    """Speak a sentence with Timbre, then transcribe it with Prisma - proves both APIs work."""
    phrase = config.SELF_TEST_PHRASES[lang_code]
    try:
        wav = client.synthesize(phrase, lang_code)
        res = client.transcribe(wav, lang_code)
    except GnaniError as e:
        st.error(f"Gnani test failed: {friendly(e)}")
        return
    st.success(f"Timbre spoke it and Prisma heard: {res.transcript!r} ({res.latency_s:.1f}s)")
    st.audio(wav, format="audio/wav")


def friendly(e: GnaniError) -> str:
    hint = ERROR_HINTS.get(e.kind, "")
    return f"{hint} ({e})" if hint else str(e)


# ------------------------------------------------------------------------------------------
# Conversation plumbing
# ------------------------------------------------------------------------------------------
def speak(client: GnaniClient | None, reply: Reply, lang_code: str, enabled: bool, model: str, voice: str) -> bytes | None:
    if not (client and enabled):
        return None
    key = (lang_code, model, voice, reply.speech)
    cache = st.session_state.tts_cache
    if key in cache:
        return cache[key]
    t0 = time.perf_counter()
    try:
        audio = client.synthesize(reply.speech, lang_code, model=model, voice=voice or None)
    except GnaniError as e:
        notify(f"Voice reply unavailable: {friendly(e)}")
        return None
    st.session_state.tts_latency = time.perf_counter() - t0
    cache[key] = audio
    return audio


def add_bot(reply: Reply, audio: bytes | None, autoplay: bool) -> None:
    ss = st.session_state
    ss.chat.append({"role": "assistant", "text": reply.text, "audio": audio, "noted": reply.noted})
    if autoplay and audio:
        ss.autoplay_idx = len(ss.chat) - 1


def user_turn(text: str, client, lang_code, speak_on, model, voice) -> None:
    ss = st.session_state
    ss.chat.append({"role": "user", "text": text, "audio": None, "noted": {}})
    reply = ss.dialogue.handle(text)
    add_bot(reply, speak(client, reply, lang_code, speak_on, model, voice), autoplay=True)


def new_conversation(lang_code, client, speak_on, model, voice, topics=None) -> None:
    ss = st.session_state
    ss.dialogue = Dialogue(lang_code, topics=topics)
    ss.chat = []
    ss.mic_n += 1
    ss.form_n += 1
    ss.last_audio_hash = None
    ss.autoplay_idx = None
    reply = ss.dialogue.start()
    add_bot(reply, speak(client, reply, lang_code, speak_on, model, voice), autoplay=False)


# ------------------------------------------------------------------------------------------
# Rendering
# ------------------------------------------------------------------------------------------
def fact_text(value, lang: str) -> str:
    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value:,}" if value >= 1000 else str(value)
    return i18n.VALUE_WORDS.get(value, i18n.VALUE_WORDS[None])[lang]


def render_chat(lang: str) -> None:
    ss = st.session_state
    for i, m in enumerate(ss.chat):
        with st.chat_message(m["role"], avatar="🌾" if m["role"] == "assistant" else "🙂"):
            st.write(m["text"])
            if m["role"] == "assistant" and m["noted"]:
                bits = [f"{i18n.SLOT_LABELS[k][lang]}: {fact_text(v, lang)}" for k, v in m["noted"].items() if k in i18n.SLOT_LABELS]
                if bits:
                    st.caption(f"{i18n.t(i18n.MESSAGES, 'noted', lang)} - " + "; ".join(bits))
            if m.get("audio"):
                st.audio(m["audio"], format="audio/wav", autoplay=(ss.autoplay_idx == i))
    ss.autoplay_idx = None  # autoplay once only


def render_result(r: SchemeResult, lang: str) -> None:
    sc = r.scheme
    with st.container(border=True):
        cls, label = {
            ELIGIBLE: ("ss-ok", i18n.UI["eligible"][lang]),
            NOT_ELIGIBLE: ("ss-no", i18n.UI["not_eligible"][lang]),
            CHECK: ("ss-chk", i18n.UI["check"][lang]),
        }[r.status]
        st.markdown(f"**{sc.name[lang]}** &nbsp; <span class='ss-status {cls}'>{label}</span>", unsafe_allow_html=True)
        if r.status == NOT_ELIGIBLE:
            st.write("**" + i18n.UI["why"][lang] + ":** " + " ".join(c.fail[lang] for c in r.failed))
        else:
            st.write(sc.benefit[lang])
            if r.status == CHECK:
                st.caption(i18n.t(i18n.MESSAGES, "summary_check", lang, names=sc.name[lang]))
            st.write("**" + i18n.UI["documents"][lang] + ":** " + "; ".join(sc.documents[lang]))
            st.write("**" + i18n.UI["how_to_apply"][lang] + ":** " + sc.apply[lang])
        if sc.note.get(lang):
            st.caption(f"{i18n.UI['note'][lang]}: {sc.note[lang]}")
        st.markdown(f"[{i18n.UI['official_source'][lang]}]({sc.source})")


def render_results(results: list[SchemeResult], lang: str) -> None:
    order = {ELIGIBLE: 0, CHECK: 1, NOT_ELIGIBLE: 2}
    for r in sorted(results, key=lambda x: order[x.status]):
        render_result(r, lang)


def render_corrections(d: Dialogue, lang: str, client, speak_on, model, voice) -> None:
    ss = st.session_state
    with st.expander(i18n.UI["your_details"][lang]):
        for slot in SLOT_ORDER:
            if slot in d.facts:
                st.write(f"- {i18n.SLOT_LABELS[slot][lang]}: **{fact_text(d.facts[slot], lang)}**")
        if not d.facts:
            st.caption(i18n.VALUE_WORDS[None][lang])
    if not d.facts:
        return
    with st.expander(i18n.UI["correct"][lang]):
        with st.form(f"fix_{ss.form_n}"):
            choices = {
                "keep": "-",
                "yes": i18n.VALUE_WORDS[True][lang],
                "no": i18n.VALUE_WORDS[False][lang],
                "unsure": i18n.VALUE_WORDS["unsure"][lang],
            }
            new_vals: dict[str, object] = {}
            for slot in SLOT_ORDER:
                if slot not in d.facts:
                    continue
                label = i18n.SLOT_LABELS[slot][lang]
                cur = d.facts[slot]
                if slot in NUMERIC_RANGES:
                    lo, hi, fallback, step = NUMERIC_RANGES[slot]
                    default = cur if isinstance(cur, int) and not isinstance(cur, bool) else fallback
                    new_vals[slot] = st.number_input(label, lo, hi, int(default), step=step, key=f"fix_{slot}_{ss.form_n}")
                else:
                    pick = st.selectbox(label, list(choices), format_func=choices.get, key=f"fix_{slot}_{ss.form_n}")
                    new_vals[slot] = pick
            submitted = st.form_submit_button(i18n.UI["apply_changes"][lang])
        if submitted:
            changes: dict[str, object] = {}
            for slot, v in new_vals.items():
                if slot in NUMERIC_RANGES:
                    if d.facts.get(slot) != v:
                        changes[slot] = int(v)
                elif v == "yes":
                    changes[slot] = True
                elif v == "no":
                    changes[slot] = False
                elif v == "unsure":
                    changes[slot] = UNSURE
            if changes:
                reply = d.apply_corrections(changes)
                add_bot(reply, speak(client, reply, d.language_code, speak_on, model, voice), autoplay=False)
                ss.form_n += 1
                st.rerun()


# ------------------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------------------
def main() -> None:
    init_state()
    ss = st.session_state
    env_key = config.get_api_key()

    with st.sidebar:
        lang_code = st.selectbox("Language / भाषा / భాష / ಭಾಷೆ", list(config.LANGUAGES), format_func=config.LANGUAGES.get, key="lang_code")
        lang = config.SHORT[lang_code]
        picked = st.multiselect(
            i18n.UI["topics"][lang], list(TOPICS), default=list(TOPICS),
            format_func=lambda t: i18n.UI[f"topic_{t}"][lang], key="topics_sel")
        topics = None if (not picked or set(picked) == set(TOPICS)) else frozenset(picked)
        speak_on = st.toggle(i18n.UI["speak_replies"][lang], value=True)
        api_key = env_key
        if not env_key:
            api_key = st.text_input("Gnani API key", type="password", help="Used only in this browser session.").strip()
        if env_key or api_key:
            st.success("Gnani API key found: Prisma (speech-to-text) and Timbre (text-to-speech) are on.")
            if st.button("Test Gnani connection", use_container_width=True):
                run_connection_test(get_client(api_key), lang_code)
        with st.expander("Advanced"):
            model = st.selectbox("TTS model", ["timbre-v2.5", "timbre-v3.0"], index=0)
            voice = st.text_input("Voice (blank = default for the language)", value="")
        if st.button(i18n.UI["start_over"][lang], use_container_width=True):
            ss.dialogue = None
        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("STT", f"{ss.stt_latency:.1f}s" if ss.stt_latency else "-")
        c2.metric("TTS", f"{ss.tts_latency:.1f}s" if ss.tts_latency else "-")

    client = get_client(api_key)

    # (Re)start the conversation on first load, language change, or "Start over".
    if ss.dialogue is None or ss.dialogue.language_code != lang_code or ss.dialogue.topics != topics:
        new_conversation(lang_code, client, speak_on, model, voice, topics)

    d: Dialogue = ss.dialogue

    st.title(i18n.UI["title"][lang])
    st.write(i18n.UI["tagline"][lang])
    if client is None:
        st.info(i18n.UI["no_key"][lang])

    # ---- input handling happens before rendering so new messages appear immediately --------
    if not d.done:
        audio_file = None
        if client is not None:
            audio_file = st.audio_input(i18n.UI["speak"][lang], key=f"mic_{ss.mic_n}", sample_rate=16000)
        typed = st.chat_input(i18n.UI["type"][lang])

        if audio_file is not None:
            data = audio_file.getvalue()
            h = hashlib.sha1(data).hexdigest()
            if h != ss.last_audio_hash:
                ss.last_audio_hash = h
                try:
                    with st.spinner("..."):
                        res = client.transcribe(data, lang_code)
                    ss.stt_latency = res.latency_s
                    if res.transcript:
                        user_turn(res.transcript, client, lang_code, speak_on, model, voice)
                    else:
                        reply = Reply(i18n.t(i18n.MESSAGES, "no_speech", lang), i18n.t(i18n.MESSAGES, "no_speech", lang))
                        add_bot(reply, speak(client, reply, lang_code, speak_on, model, voice), autoplay=True)
                except GnaniError as e:
                    notify(f"{i18n.UI['stt_failed'][lang]} {friendly(e)}")
                ss.mic_n += 1
                st.rerun()
        if typed:
            user_turn(typed, client, lang_code, speak_on, model, voice)
            st.rerun()

    if ss.notice:
        level, msg = ss.notice
        (st.warning if level == "warning" else st.error)(msg)
        ss.notice = None

    render_chat(lang)

    if d.done and d.results:
        st.subheader("✔")
        render_results(d.results, lang)
        st.caption(i18n.UI["disclaimer"][lang].format(date=_rules_date()))

    render_corrections(d, lang, client, speak_on, model, voice)
    st.caption("Voice powered by Gnani.ai: Prisma (speech-to-text) and Timbre (text-to-speech).")

    if d.done:
        st.chat_input(i18n.UI["type"][lang], disabled=True)


def _rules_date() -> str:
    import json
    try:
        return json.loads(config.SCHEMES_FILE.read_text(encoding="utf-8")).get("last_verified", "")
    except (OSError, ValueError):
        return ""


main()
