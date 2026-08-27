from search import search_web
from weather import get_weather

# Tool definitions in OpenAI/Groq function-calling format
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information on any topic. Use this for general research questions, news, facts, comparisons, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the web",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current live weather (temperature, humidity, wind speed) for a specific city or place. Use this ONLY for weather-related questions about a specific location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "place": {
                        "type": "string",
                        "description": "The city or place name to get weather for, e.g. 'Mumbai' or 'Borivali'",
                    }
                },
                "required": ["place"],
            },
        },
    },
]

def execute_tool(tool_name: str, arguments: dict):
    """
    Executes the tool the LLM decided to call, and returns the result.
    """
    if tool_name == "search_web":
        return search_web(arguments.get("query", ""))
    elif tool_name == "get_weather":
        return {"weather_summary": get_weather(arguments.get("place", ""))}
    else:
        return {"error": f"Unknown tool: {tool_name}"}