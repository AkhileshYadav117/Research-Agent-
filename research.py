import os
import re
import time
import json
from dotenv import load_dotenv
from openai import OpenAI
from search import search_web
from weather import get_weather
from decompose import decompose_query
from groq_cache import get_cached_response, set_cached_response

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "qwen/qwen3.6-27b"

def strip_thinking(text: str) -> str:
    if not text:
        return text
    if "<think>" in text and "</think>" not in text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()

def call_groq(prompt: str, max_tokens: int = 3000, temperature: float = 0.3) -> str:
    cached = get_cached_response(prompt)
    if cached is not None:
        return cached

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
        reasoning_effort="none",   # disable thinking tokens — saves budget for actual answer
    )
    result = response.choices[0].message.content or ""
    result = strip_thinking(result)
    if result:
        set_cached_response(prompt, result)
    return result

def build_fallback_answer(query: str, results: list[dict]) -> str:
    lines = [f"Here's what the top sources say about \"{query}\":\n"]
    for i, r in enumerate(results, start=1):
        snippet = r["content"][:250].strip()
        if snippet:
            lines.append(f"**[{i}]** {snippet}...")
    lines.append("\n*AI synthesis was unavailable — showing source excerpts instead.*")
    return "\n\n".join(lines)

def run_research(query: str, progress_callback=None) -> dict:
    def notify(msg: str):
        if progress_callback:
            progress_callback(msg)
    tool_calls = []

    notify("🧩 Decomposing your query into sub-questions...")
    tool_calls.append("query_decomposition")
    sub_questions = decompose_query(query)

    notify("🌐 Searching the web for relevant sources...")
    tool_calls.append("web_search")
    all_results = []
    seen_urls = set()

    for sq in sub_questions:
        sq_results = search_web(sq, max_results=7)
        for r in sq_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)

    results = all_results[:8]

    if not results:
        return {
            "answer": "No search results were found for this query.",
            "report": "",
            "sources": [],
            "tool_calls": tool_calls,
            "sub_questions": sub_questions,
        }

    weather_note = ""
    if "weather" in query.lower():
        tool_calls.append("weather_api")
        place = query.lower().replace("what is todays weather in", "").replace("weather in", "").strip("? ")
        live_weather = get_weather(place)
        if live_weather:
            weather_note = f"\n\nVERIFIED LIVE DATA (use this for exact figures):\n{live_weather}\n"

    # Context for short answer — top 3 results, 800 chars each (~600 tokens)
    short_context = "\n\n---\n\n".join(
        f"[{i+1}] {r['title']}\nContent: {r['content'][:800]}"
        for i, r in enumerate(results[:3])
        if len(r['content']) > 60
    )

    # Context for full report — top 5 results, 1200 chars each (~1500 tokens)
    report_context = "\n\n---\n\n".join(
        f"[{i+1}] {r['title']}\nURL: {r['url']}\nContent: {r['content'][:1200]}"
        for i, r in enumerate(results[:5])
        if len(r['content']) > 60
    )

    # --- Short answer for the screen ---
    short_prompt = (
         "You are a research assistant. Using ONLY the search results below, "
    "write a MEDIUM-LENGTH, detailed, and engaging answer to the user's query — "
    "3 to 4 well-developed paragraphs. Each paragraph should cover a distinct "
    "aspect of the topic: background/context, key findings, important details, "
    "and implications. Be informative and accurate. "
    "Do not write a full report — but go beyond a quick summary.\n\n"
    "HARD RULES:\n"
    "1. Only state numbers/statistics/dates that are EXPLICITLY in the "
    "search results — never invent or estimate figures.\n"
    "2. Use inline citations like [1], [2] matching the numbered sources.\n"
    "3. If exact figures aren't available, describe things qualitatively "
    "instead of guessing.\n"
    "4. Do not include headers, bullet lists, or a sources section — "
    "just flowing, well-written paragraphs.\n\n"
    f"User query: {query}\n"
    f"{weather_note}\n"
    f"Search results:\n{short_context}\n\n"
    "Now write the medium-length detailed answer:"
    )

    notify("✍️ Writing the summary answer...")
    tool_calls.append("groq_llm_synthesis")

    try:
        answer = call_groq(short_prompt, max_tokens=700, temperature=0.4)
        if not answer:
            raise ValueError("Empty response from model")
        verification = {"verified": True, "notes": "Short answer generated from grounded sources."}
    except Exception as short_err:
        answer = build_fallback_answer(query, results)
        verification = {"verified": False, "notes": f"AI synthesis unavailable ({str(short_err)[:100]}). Showing source excerpts instead."}

    # --- Detailed report for saved files ---
    notify("📄 Generating the detailed report...")
    tool_calls.append("report_generation")
    time.sleep(3)  # avoid hitting TPM rate limit between calls

    report_prompt = (
    "You are a strict, accuracy-first research analyst writing a COMPREHENSIVE, "
    "in-depth research report using ONLY information EXPLICITLY in the search "
    "results below. The report must be long, thorough, and highly informative — "
    "aim for at least 1200 words in the report body.\n\n"
    "HARD RULES:\n"
    "1. NEVER write a specific number, statistic, percentage, date, or figure "
    "unless it is EXPLICITLY stated in the search results. Do not round, estimate, "
    "or infer numbers.\n"
    "2. If a specific figure isn't available, describe qualitatively instead.\n"
    "3. Do not use outside/general knowledge to fill gaps.\n"
    "4. Use inline citations like [1], [2] matching the numbered sources.\n"
    "5. Each section must be substantive — at least 2-3 well-developed paragraphs.\n"
    "6. Use bold text (**term**) to highlight important terms and key points.\n\n"
    "Structure the report with these markdown sections (## headers):\n"
    "1. ## Executive Summary — A concise overview of the entire report (3-4 sentences)\n"
    "2. ## Background & Context — History, origin, and why this topic matters\n"
    "3. ## Key Facts & Findings — The most important verified facts and data points\n"
    "4. ## Detailed Analysis — Deep-dive into the core subject matter, broken into "
    "   sub-sections (### subheaders) covering different angles or components\n"
    "5. ## Current State & Recent Developments — What is happening right now\n"
    "6. ## Advantages & Challenges — Benefits/opportunities vs. drawbacks/risks\n"
    "7. ## Comparative Perspective — How this compares to alternatives, competitors, "
    "   or related topics (if applicable from search results)\n"
    "8. ## Expert Opinions & Stakeholder Views — Quotes or positions from experts, "
    "   organizations, or official sources mentioned in the search results\n"
    "9. ## Future Outlook & Trends — What's expected next; emerging trends\n"
    "10. ## Recommendations & Takeaways — Practical advice for different audiences\n\n"
    "IMPORTANT: Write each section fully. Do NOT skip sections or write one-liners. "
    "If a section cannot be fully addressed from the search results, use whatever "
    "relevant information is available and note the limitation.\n"
    "Do NOT include a numbered sources list at the end (sources are added separately).\n\n"
    f"Topic: {query}\n"
    f"{weather_note}\n"
    f"Search results:\n{report_context}\n\n"
    "Now write the comprehensive detailed report:"
    )

    try:
        report_body = call_groq(report_prompt, max_tokens=2000, temperature=0.3)
        if not report_body:
            raise ValueError("Empty report response")
    except Exception as report_err:
        report_body = build_fallback_answer(query, results)
        tool_calls.append(f"report_generation_fallback")
        print(f"\n[DEBUG] Report generation failed: {report_err}\n")

    sources = [{"title": r["title"], "url": r["url"]} for r in results]
    sources_md = "\n".join(f"{i+1}. [{s['title']}]({s['url']})" for i, s in enumerate(sources))

    # Build the full report — short answer is embedded as the top "Quick Answer" section
    full_report = (
        f"# Research Report: {query}\n\n"
        f"---\n\n"
        f"## 📌 Quick Answer\n\n"
        f"{answer}\n\n"
        f"---\n\n"
        f"{report_body}\n\n"
        f"---\n\n"
        f"## Sources\n{sources_md}\n"
    )

    return {
        "answer": answer,
        "report": full_report,
        "sources": sources,
        "tool_calls": tool_calls,
        "sub_questions": sub_questions,
        "verification": verification,
    }