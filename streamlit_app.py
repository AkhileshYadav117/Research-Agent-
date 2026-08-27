import os
import re
import json
import time
import shutil
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
from research import run_research
from voice_web import transcribe_audio, text_to_audio_bytes
from image_gen import generate_image, is_image_request
from pdf_export import markdown_to_pdf_bytes

st.set_page_config(page_title="ResearchX", page_icon="🔎", layout="wide")

# ---------------------------------------------------------------------------
# Custom CSS — Vibrant multi-color premium theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Main background — deep space with subtle texture ── */
.stApp {
    background: radial-gradient(ellipse at top left, #0d0221 0%, #0a0a1a 40%, #040d21 100%);
    color: #e2e8f0;
    min-height: 100vh;
}

/* ── Animated gradient title ── */
h1 {
    background: linear-gradient(90deg, #f472b6, #a855f7, #3b82f6, #06b6d4, #10b981);
    background-size: 300% 300%;
    animation: gradientShift 4s ease infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800 !important;
    font-size: 2.6rem !important;
    letter-spacing: -1px;
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ── H2 — Cyan/Teal ── */
h2 {
    background: linear-gradient(90deg, #06b6d4, #10b981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700 !important;
    font-size: 1.35rem !important;
    letter-spacing: -0.3px;
    padding-bottom: 4px;
    border-bottom: 2px solid rgba(6,182,212,0.25);
}

/* ── H3 — Pink/Rose ── */
h3 {
    color: #f9a8d4 !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
}

/* ── Input box — Teal glow ── */
.stTextInput > div > div > input {
    background: rgba(6,182,212,0.07) !important;
    border: 1.5px solid #0e7490 !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    padding: 12px 18px !important;
    font-size: 0.97rem !important;
    transition: all 0.25s ease;
}
.stTextInput > div > div > input:focus {
    border-color: #06b6d4 !important;
    box-shadow: 0 0 0 3px rgba(6,182,212,0.2), 0 0 20px rgba(6,182,212,0.1) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #4b6a7a !important;
}

/* ── Labels ── */
label, .stTextInput label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ── Research button — Hot Pink → Orange ── */
.stFormSubmitButton > button,
.stFormSubmitButton > button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg, #ec4899, #f97316) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 32px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(236, 72, 153, 0.45) !important;
    text-transform: uppercase !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 28px rgba(236, 72, 153, 0.6) !important;
}

/* ── Primary buttons (Yes continue, etc) — Purple → Blue ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #8b5cf6, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(139, 92, 246, 0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 22px rgba(139, 92, 246, 0.55) !important;
}

/* ── Secondary buttons (No I'm done, sidebar history) — Slate ── */
.stButton > button:not([kind="primary"]) {
    background: rgba(30, 41, 59, 0.8) !important;
    color: #94a3b8 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    backdrop-filter: blur(8px);
}
.stButton > button:not([kind="primary"]):hover {
    background: rgba(51, 65, 85, 0.9) !important;
    color: #e2e8f0 !important;
    border-color: #64748b !important;
    transform: translateY(-1px) !important;
}

/* ── Download .md — Blue ── */
.stDownloadButton:nth-of-type(1) > button {
    background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(59,130,246,0.35) !important;
    transition: all 0.2s ease !important;
}
/* ── Download .txt — Emerald ── */
.stDownloadButton:nth-of-type(2) > button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(16,185,129,0.35) !important;
    transition: all 0.2s ease !important;
}
/* ── Download .pdf — Amber/Orange ── */
.stDownloadButton:nth-of-type(3) > button {
    background: linear-gradient(135deg, #d97706, #f59e0b) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(245,158,11,0.35) !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    filter: brightness(1.1) !important;
}

/* ── Expander — Glassmorphism dark ── */
.streamlit-expanderHeader {
    background: rgba(15, 23, 42, 0.7) !important;
    border: 1px solid rgba(6,182,212,0.25) !important;
    border-radius: 12px !important;
    color: #67e8f9 !important;
    font-weight: 600 !important;
    backdrop-filter: blur(10px);
    transition: background 0.2s ease !important;
}
.streamlit-expanderHeader:hover {
    background: rgba(6,182,212,0.08) !important;
}
.streamlit-expanderContent {
    background: rgba(7, 15, 30, 0.85) !important;
    border: 1px solid rgba(6,182,212,0.2) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    backdrop-filter: blur(10px);
}

/* ── Status box — Teal glow ── */
[data-testid="stStatusWidget"] {
    background: rgba(6,182,212,0.06) !important;
    border: 1px solid rgba(6,182,212,0.3) !important;
    border-radius: 14px !important;
    box-shadow: 0 0 30px rgba(6,182,212,0.08) !important;
}

/* ── Success alert — Emerald ── */
[data-testid="stAlert"][class*="success"] {
    background: rgba(16,185,129,0.1) !important;
    border-left: 4px solid #10b981 !important;
    border-radius: 10px !important;
    color: #6ee7b7 !important;
}
/* ── Warning alert — Amber ── */
[data-testid="stAlert"][class*="warning"] {
    background: rgba(245,158,11,0.1) !important;
    border-left: 4px solid #f59e0b !important;
    border-radius: 10px !important;
    color: #fcd34d !important;
}
/* ── Error alert — Rose ── */
[data-testid="stAlert"][class*="error"] {
    background: rgba(244,63,94,0.1) !important;
    border-left: 4px solid #f43f5e !important;
    border-radius: 10px !important;
    color: #fda4af !important;
}
/* ── Info alert — Blue ── */
[data-testid="stAlert"][class*="info"] {
    background: rgba(59,130,246,0.08) !important;
    border-left: 4px solid #3b82f6 !important;
    border-radius: 10px !important;
    color: #93c5fd !important;
}

/* ── Sidebar — Deep Blue gradient ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #030712 0%, #0a0f2e 50%, #030f21 100%) !important;
    border-right: 1px solid rgba(59,130,246,0.2) !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2 {
    background: linear-gradient(90deg, #60a5fa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: rgba(15, 23, 42, 0.7) !important;
    color: #93c5fd !important;
    border: 1px solid rgba(59,130,246,0.2) !important;
    border-radius: 8px !important;
    width: 100% !important;
    text-align: left !important;
    margin-bottom: 5px !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    transition: all 0.2s ease !important;
    padding: 8px 12px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59,130,246,0.15) !important;
    color: #bfdbfe !important;
    border-color: rgba(59,130,246,0.5) !important;
    transform: translateX(3px) !important;
}

/* ── Divider — multicolor gradient line ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, #8b5cf6, #06b6d4, #10b981, transparent) !important;
    opacity: 0.6 !important;
    margin: 16px 0 !important;
}

/* ── Audio player ── */
audio {
    border-radius: 10px !important;
    width: 100% !important;
    filter: hue-rotate(200deg) saturate(0.8);
}

/* ── Caption ── */
.stCaption, small {
    color: #475569 !important;
    font-size: 0.78rem !important;
}

/* ── Spinner text ── */
.stSpinner > div > div {
    border-top-color: #f472b6 !important;
}

/* ── Markdown text ── */
.stMarkdown p {
    color: #cbd5e1 !important;
    line-height: 1.75 !important;
}
.stMarkdown strong {
    color: #f9a8d4 !important;
    font-weight: 600 !important;
}
.stMarkdown a {
    color: #38bdf8 !important;
    text-decoration: none !important;
    border-bottom: 1px solid rgba(56,189,248,0.3);
    transition: border-color 0.2s ease;
}
.stMarkdown a:hover {
    border-bottom-color: #38bdf8;
}
.stMarkdown code {
    background: rgba(139,92,246,0.15) !important;
    color: #c4b5fd !important;
    border-radius: 4px !important;
    padding: 1px 5px !important;
    font-size: 0.85em !important;
}
</style>
""", unsafe_allow_html=True)




def save_report(report_text: str, query: str) -> tuple[str, str]:
    os.makedirs("reports", exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", query.strip())[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = f"reports/{safe_name}_{timestamp}"

    md_path = f"{base_path}.md"
    txt_path = f"{base_path}.txt"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return md_path, txt_path

HISTORY_FILE = "history.json"

def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history: list) -> None:
    try:
        # Only save serializable fields (no raw image bytes)
        safe_history = []
        for item in history:
            safe_item = {k: v for k, v in item.items() if k != "image_bytes"}
            safe_history.append(safe_item)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(safe_history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = load_history()
if "session_active" not in st.session_state:
    st.session_state.session_active = True
if "awaiting_continue" not in st.session_state:
    st.session_state.awaiting_continue = False
if "research_time" not in st.session_state:
    st.session_state.research_time = None

# ---------------------------------------------------------------------------
# Sidebar: Stats + Clear Cache + Search + Past queries
# ---------------------------------------------------------------------------

with st.sidebar:
    # ── Feature 10: Stats Dashboard ──
    total_queries   = len(st.session_state.history)
    total_images    = sum(1 for h in st.session_state.history if h.get("is_image"))
    total_research  = total_queries - total_images
    cache_files     = len(os.listdir("groq_cache")) if os.path.isdir("groq_cache") else 0

    st.markdown("""
    <div style='
        background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1));
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 14px;
    '>
        <div style='color:#94a3b8; font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>📊 Session Stats</div>
        <div style='display:flex; gap:8px; flex-wrap:wrap;'>
            <div style='flex:1; background:rgba(6,182,212,0.1); border-radius:10px; padding:8px; text-align:center; min-width:55px;'>
                <div style='color:#67e8f9; font-size:1.3rem; font-weight:700;'>""" + str(total_research) + """</div>
                <div style='color:#94a3b8; font-size:0.65rem;'>Research</div>
            </div>
            <div style='flex:1; background:rgba(244,63,94,0.1); border-radius:10px; padding:8px; text-align:center; min-width:55px;'>
                <div style='color:#fda4af; font-size:1.3rem; font-weight:700;'>""" + str(total_images) + """</div>
                <div style='color:#94a3b8; font-size:0.65rem;'>Images</div>
            </div>
            <div style='flex:1; background:rgba(16,185,129,0.1); border-radius:10px; padding:8px; text-align:center; min-width:55px;'>
                <div style='color:#6ee7b7; font-size:1.3rem; font-weight:700;'>""" + str(cache_files) + """</div>
                <div style='color:#94a3b8; font-size:0.65rem;'>Cached</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature 6: Clear Cache Button ──
    st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)
    col_cache, col_hist = st.columns(2)
    with col_cache:
        if st.button("🗑️ Clear Cache", help="Delete all cached AI responses"):
            if os.path.isdir("groq_cache"):
                shutil.rmtree("groq_cache")
                os.makedirs("groq_cache", exist_ok=True)
            st.success("Cache cleared!")
            st.rerun()
    with col_hist:
        if st.button("🧹 Clear History", help="Delete all past queries from sidebar"):
            st.session_state.history = []
            save_history([])
            if "selected" in st.session_state:
                del st.session_state["selected"]
            st.rerun()

    st.divider()

    # ── Feature 7: Search History ──
    st.markdown("<div style='color:#94a3b8; font-size:0.75rem; font-weight:600; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px;'>🔍 Past Queries</div>", unsafe_allow_html=True)

    history_search = st.text_input(
        "Search history",
        placeholder="Filter queries...",
        label_visibility="collapsed",
        key="history_search"
    )

    filtered_history = [
        h for h in st.session_state.history
        if not history_search or history_search.lower() in h.get("query", "").lower()
    ]

    if not filtered_history:
        if history_search:
            st.caption("No matching queries found.")
        else:
            st.caption("Nothing yet — run a query to see it here.")

    # ── Feature 9: Delete individual history items ──
    for past in filtered_history:
        col_q, col_del = st.columns([5, 1])
        with col_q:
            label = ("🖼️ " if past.get("is_image") else "🔎 ") + past["query"][:38]
            if st.button(label, key=f"hist_{past['timestamp']}"):
                st.session_state.selected = past
                st.session_state.awaiting_continue = True
                st.rerun()
        with col_del:
            if st.button("✕", key=f"del_{past['timestamp']}", help="Remove this query"):
                st.session_state.history = [
                    h for h in st.session_state.history
                    if h["timestamp"] != past["timestamp"]
                ]
                save_history(st.session_state.history)
                if st.session_state.get("selected", {}).get("timestamp") == past["timestamp"]:
                    if "selected" in st.session_state:
                        del st.session_state["selected"]
                st.rerun()

# ---------------------------------------------------------------------------
# Main input
# ---------------------------------------------------------------------------

st.title("🔎 ResearchX")

if not st.session_state.session_active:
    st.info("Session ended. Refresh the page to start a new research session.")
    st.caption("⚠️ ResearchX is AI and can make mistakes.")
    st.stop()

if not st.session_state.awaiting_continue:
    st.subheader("🎙️ Ask by voice")
    audio_value = st.audio_input("Record your question")

    voice_query = None
    if audio_value is not None:
        with st.spinner("Transcribing your question..."):
            voice_query = transcribe_audio(audio_value.getvalue())
        if voice_query:
            st.success(f'Heard: "{voice_query}"')
        else:
            st.warning("Could not understand the audio. Try again or type below.")

    st.subheader("⌨️ Or type your question")

    with st.form(key="research_form", clear_on_submit=True):
        query_input = st.text_input(
            "What do you want to research?",
            placeholder="e.g. What's the current state of solid-state batteries?",
            value=voice_query if voice_query else "",
        )
        run_clicked = st.form_submit_button("🔎 Research", type="primary")

    query = query_input.strip()

    if run_clicked:
        if not query:
            st.warning("Please enter a question first.")
            st.stop()

        if is_image_request(query):
            with st.spinner("Generating your image..."):
                image_bytes = generate_image(query)

            result = {
                "is_image": True,
                "image_bytes": image_bytes,
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "answer": f'Generated image for: "{query}"',
                "sources": [],
                "sub_questions": [],
                "tool_calls": ["image_generation"],
                "verification": None,
                "report": "",
                "md_path": "",
                "txt_path": "",
            }
        else:
            # Feature 8: Research Timer
            _t_start = time.time()
            with st.status("🔎 Researching your query...", expanded=True) as status:
                def update_status(msg: str):
                    status.write(msg)

                result = run_research(query, progress_callback=update_status)
                md_path, txt_path = save_report(result["report"], query)
                result["timestamp"] = datetime.now().isoformat()
                result["query"] = query
                result["md_path"] = md_path
                result["txt_path"] = txt_path
                result["is_image"] = False
                _elapsed = round(time.time() - _t_start, 1)
                result["research_time"] = _elapsed
                status.update(label=f"✅ Research complete! ({_elapsed}s)", state="complete", expanded=False)

        st.session_state.history.insert(0, result)
        save_history(st.session_state.history)
        st.session_state.selected = result
        st.session_state.awaiting_continue = True
        st.rerun()


# ---------------------------------------------------------------------------
# Display selected result
# ---------------------------------------------------------------------------

result = st.session_state.get("selected")

if result and result.get("is_image"):
    st.subheader("Generated Image")

    if result["image_bytes"]:
        st.image(result["image_bytes"], caption=result["query"], use_container_width=True)
        st.download_button(
            "Download image",
            data=result["image_bytes"],
            file_name=f"generated_{re.sub(r'[^a-zA-Z0-9]+', '_', result['query'])[:40]}.png",
            mime="image/png",
        )
    else:
        st.error("Sorry, image generation failed. Please try again.")

elif result:
    st.subheader("Sub-questions researched")
    for i, sq in enumerate(result.get("sub_questions", []), start=1):
        st.markdown(f"**{i}.** {sq}")

    st.subheader("Answer")
    st.markdown(result["answer"])

    # Feature 8: Word count + reading time + research timer
    word_count = len(result["answer"].split())
    read_time = max(1, round(word_count / 200))
    research_secs = result.get("research_time", None)
    timer_str = f" · 🕐 {research_secs}s research" if research_secs else ""
    st.caption(f"📝 {word_count} words · ⏱️ ~{read_time} min read{timer_str}")

    # Copy to clipboard button
    import json as _json
    safe_text = _json.dumps(result["answer"])[1:-1]  # JSON-encode then strip outer quotes
    components.html(f"""
    <div style="margin: 6px 0 12px 0;">
        <button id="copyBtn" onclick="copyAnswer()" style="
            background: linear-gradient(135deg, #0891b2, #06b6d4);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            font-family: Inter, sans-serif;
            letter-spacing: 0.3px;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(6,182,212,0.35);
        ">
            📋 Copy Answer
        </button>
        <span id="copyMsg" style="
            margin-left: 10px;
            color: #10b981;
            font-size: 13px;
            font-family: Inter, sans-serif;
            opacity: 0;
            transition: opacity 0.3s ease;
        ">Copied!</span>
    </div>
    <script>
        function copyAnswer() {{
            const text = "{safe_text}";
            navigator.clipboard.writeText(text).then(function() {{
                const msg = document.getElementById('copyMsg');
                msg.style.opacity = '1';
                document.getElementById('copyBtn').innerText = '✅ Copied!';
                setTimeout(() => {{
                    msg.style.opacity = '0';
                    document.getElementById('copyBtn').innerText = '📋 Copy Answer';
                }}, 2000);
            }});
        }}
    </script>
    """, height=60)

    with st.spinner("Generating audio..."):
        audio_bytes = text_to_audio_bytes(result["answer"])
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")

    verification = result.get("verification")
    if verification:
        if verification["verified"]:
            st.success(f"✅ Verified — {verification['notes']}")
        else:
            st.warning(f"⚠️ Needs review — {verification['notes']}")

    with st.expander("Agent trace (tool calls)"):
        for tc in result["tool_calls"]:
            st.markdown(f"→ `{tc}`")

    st.subheader("Sources")
    if result["sources"]:
        for i, s in enumerate(result["sources"], start=1):
            st.markdown(f"**[{i}]** [{s['title']}]({s['url']})")
    else:
        st.caption("No sources found.")

    st.subheader("Full report")
    with st.expander("View full report", expanded=False):
        st.markdown(result["report"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "📄 Download .md",
            data=result["report"],
            file_name=os.path.basename(result["md_path"]),
            mime="text/markdown",
        )
    with col2:
        st.download_button(
            "📝 Download .txt",
            data=result["report"],
            file_name=os.path.basename(result["txt_path"]),
            mime="text/plain",
        )
    with col3:
        pdf_name = os.path.basename(result["md_path"]).replace(".md", ".pdf")
        pdf_bytes = markdown_to_pdf_bytes(result["report"])
        st.download_button(
            "📅 Download .pdf",
            data=pdf_bytes,
            file_name=pdf_name,
            mime="application/pdf",
        )

    st.caption(f"Saved to `{result['md_path']}` and `{result['txt_path']}`")

else:
    st.info("Enter a query above and click Research to get started.")

# ---------------------------------------------------------------------------
# Continue or stop (applies to both research and image results)
# ---------------------------------------------------------------------------
if result and st.session_state.awaiting_continue:
    st.divider()
    st.subheader("Anything else you want to research?")
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Yes, continue researching", type="primary"):
            st.session_state.awaiting_continue = False
            st.rerun()
    with col_no:
        if st.button("No, I'm done"):
            st.session_state.session_active = False
            st.rerun()
