import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

def decompose_query(query: str) -> list[str]:
    """
    Breaks a broad research query into 2-3 focused sub-questions.
    Falls back to the original query if decomposition fails.
    """
    prompt = (
        "Break the following research query into 4-5 focused, specific "
        "sub-questions that together would give a complete answer. "
        "Respond ONLY with a JSON array of strings, nothing else.\n\n"
        f"Query: {query}\n\n"
        'Example format: ["sub-question 1", "sub-question 2", "sub-question 3"]'
    )

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3,
            reasoning_effort="low",
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.replace("json", "", 1).strip()

        sub_questions = json.loads(raw)

        if isinstance(sub_questions, list) and len(sub_questions) > 0:
            return sub_questions[:5]
    except Exception:
        pass

    return [query]