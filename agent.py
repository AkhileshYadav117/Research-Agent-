import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import TOOL_DEFINITIONS, execute_tool

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

def run_agent(query: str) -> dict:
    """
    Runs a true agent loop: the LLM decides which tools to call,
    we execute them, and feed results back until it gives a final answer.
    """
    tool_calls_log = []
    sources = []

    messages = [
        {"role": "system",
            "content": (
                "You are a research assistant with access to tools. Use "
                "search_web for general questions and get_weather for "
                "weather-specific questions about a location. Call search_web "
                "AT MOST 2 times total, then STOP calling tools and give your "
                "final answer using what you've found. After gathering "
                "information, give a clear, concise answer (3-5 sentences) "
                "citing sources like [1], [2] where relevant."
            ),

        },
        {"role": "user", "content": query},
    ]

    max_turns = 6

    for turn in range(max_turns):
        is_last_turn = turn == max_turns - 1
        tool_choice = "none" if is_last_turn else "auto"

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice=tool_choice,
            max_tokens=800,
            temperature=0.3,
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                # Safety: strip any stray channel markers the model sometimes leaks
                if "<|" in tool_name:
                    tool_name = tool_name.split("<|")[0]

                try:
                    arguments = json.loads(tc.function.arguments)
                except Exception:
                    arguments = {}

                tool_calls_log.append(f"{tool_name}({arguments})")

                result = execute_tool(tool_name, arguments)

                if tool_name == "search_web" and isinstance(result, list):
                    for r in result:
                        if r not in sources:
                            sources.append(r)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result)[:4000],
                    }
                )
            continue

        answer = msg.content or "(No answer generated.)"
        return {
            "answer": answer,
            "sources": [{"title": s["title"], "url": s["url"]} for s in sources],
            "tool_calls": tool_calls_log,
        }

    return {
        "answer": "The agent could not finish within the allowed steps.",
        "sources": [{"title": s["title"], "url": s["url"]} for s in sources],
        "tool_calls": tool_calls_log,
    }