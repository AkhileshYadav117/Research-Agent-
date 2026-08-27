<div align="center">

# 🔎 ResearchX

### AI-Powered Research Agent — Built with Streamlit + Groq

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-myresearchx.streamlit.app-FF4B4B?style=for-the-badge)](https://myresearchx.streamlit.app/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.62-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq%20LLM-orange?style=for-the-badge)](https://groq.com)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**ResearchX** is a full-featured AI research agent that searches the web, synthesizes information, and delivers detailed reports — all in a beautiful dark-themed UI.

### 👉 [Try it live → myresearchx.streamlit.app](https://myresearchx.streamlit.app/)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧩 **Query Decomposition** | Automatically breaks your question into focused sub-questions |
| 🌐 **Web Search** | Searches DuckDuckGo and scrapes real page content |
| 🤖 **AI Synthesis** | Powered by Groq LLM (Qwen 3) — clean paragraph answers, not raw excerpts |
| 📄 **Detailed Reports** | Full 1000+ word reports with Executive Summary, Analysis, Future Outlook, and more |
| 🎙️ **Voice Input** | Record your question by voice — auto-transcribed to text |
| 🔊 **Audio Playback** | Listen to the answer read aloud (text-to-speech) |
| 🖼️ **Image Generation** | Say "generate image of..." — uses Pollinations AI (no API key needed) |
| 📊 **Research History** | All past queries saved and browsable in the sidebar |
| 🔍 **Search History** | Filter past queries instantly |
| 🗑️ **Delete Queries** | Remove individual history entries |
| 📊 **Stats Dashboard** | Live counts of research queries, images generated, and cached responses |
| ⏱️ **Research Timer** | See exactly how long each research took |
| 📋 **Copy to Clipboard** | One-click copy of the full answer |
| 📥 **Export Reports** | Download as `.md`, `.txt`, or `.pdf` |
| 🗑️ **Clear Cache** | One-click cache reset from sidebar |
| ✅ **Answer Verification** | Each answer is graded for factual grounding |

---

## 🚀 Quick Start (Local)

### 1. Clone the repository
```bash
git clone https://github.com/AkhileshYadav117/Research-Agent-.git
cd Research-Agent-
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
```bash
# Copy the template
cp .env.example .env
```
Then open `.env` and paste your real Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```
> 🔑 Get a **free** API key at [console.groq.com](https://console.groq.com)

### 5. Run the app
```bash
streamlit run streamlit_app.py
```

Open **http://localhost:8501** in your browser. 🎉

---

## ☁️ Deploy on Streamlit Cloud (Free)

This app is live at **[myresearchx.streamlit.app](https://myresearchx.streamlit.app/)**

To deploy your own copy:
1. Fork this repo on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repo → `streamlit_app.py` → Deploy
5. In **Advanced Settings → Secrets**, add:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

---

## 🗂️ Project Structure

```
Research-Agent/
│
├── streamlit_app.py      # Main UI — Streamlit frontend
├── research.py           # Core research pipeline (decompose → search → synthesize)
├── search.py             # Web search + page scraping (DuckDuckGo)
├── decompose.py          # Query decomposition using Groq LLM
├── groq_cache.py         # Response caching (6-hour TTL)
├── pdf_export.py         # Markdown → PDF converter
├── voice_web.py          # Voice input (STT) + audio output (TTS)
├── image_gen.py          # AI image generation via Pollinations
├── weather.py            # Live weather tool
├── agent.py              # Agent loop (tool-calling architecture)
├── tools.py              # Tool definitions for the agent
│
├── requirements.txt      # Python dependencies
├── .env.example          # API key template (safe to share)
├── .gitignore            # Excludes .env, venv, cache, reports
└── .streamlit/
    └── config.toml       # Streamlit theme and server config
```

---

## 🔧 Configuration

| Variable | Description | Where to get it |
|----------|-------------|-----------------|
| `GROQ_API_KEY` | LLM API key (required) | [console.groq.com](https://console.groq.com) — Free |

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit with custom CSS (dark glassmorphism theme)
- **LLM:** Groq API — `qwen/qwen3-6b` (fast, free tier available)
- **Search:** DuckDuckGo (`ddgs`) + BeautifulSoup page scraping
- **Voice:** Google Speech Recognition + gTTS
- **Image Gen:** Pollinations.ai (100% free, no API key)
- **PDF:** fpdf2 — pure Python PDF generation
- **Caching:** Local JSON cache with 6-hour TTL

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

Made with ❤️ using **Python**, **Streamlit**, and **Groq AI**

⭐ Star this repo if you found it useful!

</div>
