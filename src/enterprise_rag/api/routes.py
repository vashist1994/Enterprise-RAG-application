import re
from math import ceil
from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, UploadFile
from enterprise_rag.api.schemas import AskRequest, AskResponse, SourceReference
from enterprise_rag.config.settings import get_settings
from enterprise_rag.ingestion.pipeline import ingest_uploaded_pdf
from enterprise_rag.workflows.graph import workflow
from enterprise_rag.observability.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/documents")
async def upload_document(file: UploadFile = File(...)) -> dict[str, str | int]:
    settings = get_settings()
    filename = (file.filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Upload a PDF file.")
    content = await file.read(settings.max_upload_size_mb * 1024 * 1024 + 1)
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF exceeds the upload size limit.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=415, detail="The uploaded file is not a valid PDF.")

    document_id = uuid4().hex
    try:
        page_count, chunk_count = ingest_uploaded_pdf(content, filename)
    except Exception as exc:
        logger.exception("document_ingestion_failed", document_id=document_id)
        retry_match = re.search(r"RESOURCE_EXHAUSTED.*?retry in ([\d.]+)s", str(exc), re.IGNORECASE)
        if retry_match:
            retry_after = ceil(float(retry_match.group(1)))
            raise HTTPException(
                status_code=429,
                detail=f"Gemini quota exceeded. Retry in about {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            ) from exc
        raise HTTPException(status_code=422,
                            detail="Could not read or index this PDF.") from exc
    return {"document_id": document_id, "filename": filename,
            "page_count": page_count, "chunk_count": chunk_count}

@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    settings = get_settings()
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question cannot be blank.")
    if len(question) > settings.max_question_length:
        raise HTTPException(status_code=413, detail="Question is too long.")
    request_id = str(uuid4())
    try:
        result = workflow.invoke({"question": question, "request_id": request_id})
        return AskResponse(request_id=request_id,
                           answer=result.get("answer", "No answer was generated."),
                           sources=[SourceReference(**s) for s in result.get("sources", [])])
    except FileNotFoundError as exc:
        logger.error("rag_index_missing", request_id=request_id)
        raise HTTPException(status_code=503, detail="Knowledge index is not ready.") from exc
    except Exception as exc:
        logger.exception("rag_request_failed", request_id=request_id)
        raise HTTPException(status_code=500,
                            detail=f"Request failed. Reference ID: {request_id}") from exc
