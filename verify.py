import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

def verify_answer(answer: str, context: str) -> dict:
    """
    Checks whether the answer is well-supported by the source context.
    Returns a dict with 'verified' (bool) and 'notes' (str).
    """
    prompt = (
        "You are a fact-checker. Below is an ANSWER and the SOURCE MATERIAL "
        "it was based on. Check if every factual claim in the ANSWER (numbers, "
        "names, dates, statistics) is actually supported by the SOURCE MATERIAL. "
        "Respond ONLY in this exact format:\n"
        "VERIFIED: yes or no\n"
        "NOTES: one short sentence explaining any unsupported claims, or 'All "
        "claims supported.' if everything checks out.\n\n"
        f"ANSWER:\n{answer}\n\n"
        f"SOURCE MATERIAL:\n{context}\n"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0,
            reasoning_effort="low",
        )
        raw = response.choices[0].message.content or ""

        verified = "verified: yes" in raw.lower()
        notes_line = ""
        for line in raw.split("\n"):
            if line.strip().lower().startswith("notes:"):
                notes_line = line.split(":", 1)[1].strip()
                break

        return {"verified": verified, "notes": notes_line or "Could not verify."}
    except Exception:
        return {"verified": False, "notes": "Verification step failed to run."}