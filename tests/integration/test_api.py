from fastapi.testclient import TestClient
from enterprise_rag.main import app
from enterprise_rag.api import routes

def test_health_endpoint():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_upload_pdf_uses_configured_namespace(monkeypatch):
    monkeypatch.setattr(routes, "ingest_uploaded_pdf", lambda content, filename: (2, 3))
    response = TestClient(app).post(
        "/api/v1/documents",
        files={"file": ("notes.pdf", b"%PDF-1.7 test", "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "notes.pdf"
    assert "namespace" not in response.json()
    assert response.json()["page_count"] == 2

def test_upload_rejects_non_pdf():
    response = TestClient(app).post(
        "/api/v1/documents",
        files={"file": ("notes.txt", b"not a PDF", "text/plain")},
    )
    assert response.status_code == 415

def test_upload_returns_retry_hint_for_gemini_quota(monkeypatch):
    def fail_ingestion(content, filename):
        raise RuntimeError(
            "RESOURCE_EXHAUSTED: quota exceeded. Please retry in 39.3s."
        )
    monkeypatch.setattr(routes, "ingest_uploaded_pdf", fail_ingestion)
    response = TestClient(app).post(
        "/api/v1/documents",
        files={"file": ("notes.pdf", b"%PDF-1.7 test", "application/pdf")},
    )
    assert response.status_code == 429
    assert response.headers["retry-after"] == "40"
    assert "Retry in about 40 seconds" in response.json()["detail"]

def test_ask_does_not_accept_namespace_argument(monkeypatch):
    seen = {}
    def invoke(payload):
        seen.update(payload)
        return {"answer": "Found it.", "sources": []}
    monkeypatch.setattr(routes.workflow, "invoke", invoke)
    response = TestClient(app).post(
        "/api/v1/ask", json={"question": "Summarize this"}
    )
    assert response.status_code == 200
    assert "namespace" not in seen
