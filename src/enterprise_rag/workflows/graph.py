from langgraph.graph import END, START, StateGraph
from enterprise_rag.rag.graph import rag_graph
from enterprise_rag.workflows.state import WorkflowState

def build_workflow():
    builder = StateGraph(WorkflowState)
    builder.add_node("rag", rag_graph)
    builder.add_edge(START, "rag")
    builder.add_edge("rag", END)
    return builder.compile()

workflow = build_workflow()
