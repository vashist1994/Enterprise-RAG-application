from enterprise_rag.workflows.graph import workflow

if __name__ == "__main__":
    print("Ask a question; type 'exit' to quit.")
    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        result = workflow.invoke({"question": question})
        # print(result)
        print(f"\nAnswer: {result.get('answer', '')[0]['text']}")
        for source in result.get("sources", []):
            print(f"- {source['source']} (page {source['page']})")
