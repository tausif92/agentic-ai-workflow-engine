from app.workflows.langgraph_workflow import build_graph


def generate_mermaid():

    graph = build_graph()

    # 🔥 This generates Mermaid syntax
    mermaid_diagram = graph.get_graph().draw_mermaid()

    print("\n--- Mermaid Diagram ---\n")
    print(mermaid_diagram)

    # Optional: Save to file
    with open("workflow_diagram.md", "w") as f:
        f.write("```mermaid\n")
        f.write(mermaid_diagram)
        f.write("\n```")


if __name__ == "__main__":
    generate_mermaid()
