from typing import TypedDict
from langchain_core.documents import Document

class WorkflowState(TypedDict, total=False):
    question: str
    request_id: str
    documents: list[Document]
    answer: str
    sources: list[dict[str, str]]
    error: str
