from langchain_core.documents import Document
from enterprise_rag.models.chat import get_chat_model
from enterprise_rag.rag.prompts import ANSWER_PROMPT
from enterprise_rag.rag.state import RAGState
from enterprise_rag.retrieval.store import retrieve
from enterprise_rag.observability.logging import get_logger

logger = get_logger(__name__)

def retrieve_node(state: RAGState) -> dict:
    docs = retrieve(state.get("question", "").strip())
    logger.info("retrieval_completed", request_id=state.get("request_id", "unknown"),
                result_count=len(docs))
    return {"documents": docs}

def generate_node(state: RAGState) -> dict:
    question = state.get("question", "").strip()
    docs: list[Document] = state.get("documents", [])
    context = "\n\n".join(
        f"[Source: {d.metadata.get('source', 'unknown')}; "
        f"Page: {d.metadata.get('page', 'n/a')}]\n{d.page_content}" for d in docs)
    sources = [{"source": str(d.metadata.get("source", "unknown")),
                "page": str(d.metadata.get("page", "n/a"))} for d in docs]
    if not context:
        return {"answer": "I couldn't find relevant information in the indexed documents.",
                "sources": []}
    result = (ANSWER_PROMPT | get_chat_model()).invoke(
        {"question": question, "context": context})
    answer = result.content #if isinstance(result.content, str) else str(result.content)
    return {"answer": answer, "sources": sources}
