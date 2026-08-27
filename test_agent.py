from agent import run_agent

def main():
    query = input("Enter your research query: ")

    print(f"\nResearching: {query}")
    print("=" * 60)

    result = run_agent(query)

    print("\nTOOL CALLS (decided by the LLM):")
    print("-" * 60)
    for tc in result["tool_calls"]:
        print(f"→ {tc}")

    print("\nANSWER:")
    print("-" * 60)
    print(result["answer"])

    print("\n" + "=" * 60)
    print("SOURCES:")
    print("-" * 60)
    if result["sources"]:
        for i, s in enumerate(result["sources"], start=1):
            print(f"[{i}] {s['title']}")
            print(f"    {s['url']}")
    else:
        print("No sources found.")

if __name__ == "__main__":
    main()