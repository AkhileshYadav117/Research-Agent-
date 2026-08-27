import re
from voice import listen, speak
from research import run_research

def clean_for_speech(text: str) -> str:
    """Removes markdown/citation symbols so speech doesn't read them out."""
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"[#*_`]", "", text)
    return text.strip()

def main():
    speak("Hello! Please ask your question.", language="en")

    print("🎙️  Listening... speak your question now.")
    query = listen(language="en")

    if not query:
        msg = "Sorry, I could not hear your question. Please try again."
        print(msg)
        speak(msg, language="en")
        return

    print(f"\nResearching: {query}")
    result = run_research(query)

    print("\nANSWER (text):")
    print(result["answer"])

    print("\nSOURCES:")
    for i, s in enumerate(result["sources"], start=1):
        print(f"[{i}] {s['title']}")
        print(f"    {s['url']}")

    speech_text = clean_for_speech(result["answer"])
    print("\n🔊 Reading the answer aloud...")
    speak(speech_text, language="en")

if __name__ == "__main__":
    main()