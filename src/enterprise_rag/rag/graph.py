from langgraph.graph import END, START, StateGraph
from enterprise_rag.rag.nodes import generate_node, retrieve_node
from enterprise_rag.rag.state import RAGState

def build_rag_graph():
    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()

rag_graph = build_rag_graph()
