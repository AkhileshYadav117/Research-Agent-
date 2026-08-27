import os
import re
from datetime import datetime
from research import run_research

def save_txt(report_text: str, filepath: str):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)

def save_md(report_text: str, filepath: str):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)

def main():
    query = input("Enter your research query: ")

    print(f"\nResearching: {query}")
    print("=" * 60)

    result = run_research(query)
    
    print("\nSUB-QUESTIONS RESEARCHED:")
    print("-" * 60)
    for i, sq in enumerate(result.get("sub_questions", []), start=1):
        print(f"{i}. {sq}")

    print("\nTOOL CALLS:")
    print("-" * 60)
    for tool in result["tool_calls"]:
        print(f"→ {tool}")

    print("\nANSWER:")
    print("-" * 60)
    print(result["answer"])

    verification = result.get("verification")
    if verification:
        status = "✓ Verified" if verification["verified"] else "⚠ Needs review"
        print(f"\n[{status}] {verification['notes']}")

    print("\n" + "=" * 60)
    print("SOURCES:")
    print("-" * 60)
    if result["sources"]:
        for i, s in enumerate(result["sources"], start=1):
            print(f"[{i}] {s['title']}")
            print(f"    {s['url']}")
    else:
        print("No sources found.")

    if result.get("report"):
        os.makedirs("reports", exist_ok=True)
        safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", query.strip())[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = f"reports/{safe_name}_{timestamp}"

        save_md(result["report"], f"{base_path}.md")
        save_txt(result["report"], f"{base_path}.txt")

        print("\n" + "=" * 60)
        print("Reports saved:")
        print(f"  {base_path}.md")
        print(f"  {base_path}.txt")

if __name__ == "__main__":
    main()