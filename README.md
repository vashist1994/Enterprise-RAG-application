# Enterprise RAG with LangGraph

Modular starter using Python 3.11+, uv, LangGraph, LangChain, Google Gemini, Pinecone, and FastAPI.

## Setup
```bash
uv sync
cp -n .env.example .env
# Add GOOGLE_API_KEY and PINECONE_API_KEY to .env
# Create a Pinecone index matching the embedding model dimensions and cosine metric.
# Set PINECONE_INDEX_NAME to that index.
```

Start the API in one terminal:
```bash
uv run uvicorn enterprise_rag.main:app --reload
```

Start the React interface in a second terminal:
```bash
cd web
npm install
npm run dev
```

Open the Vite URL printed in the terminal (usually `http://127.0.0.1:5173`), upload a PDF, then ask questions in the chat. Uploads and chat retrieval both use the Pinecone namespace configured by `PINECONE_NAMESPACE` in `.env`.

The API docs are available at `http://127.0.0.1:8000/docs`. For command-line ingestion and chat, use `uv run python scripts/ingest.py` and `uv run python scripts/ask.py`.
Tests: `uv run pytest`

## Run with Docker Compose

Create `.env` from `.env.example`, add the Google and Pinecone credentials, then run:

```bash
docker compose up --build
```

Open the UI at `http://127.0.0.1:8080`. The UI container serves the built React app and proxies `/api` and `/health` to the separate RAG API container. The API is also available locally at `http://127.0.0.1:8000` for API docs and development; uploaded documents persist in `data/`.

## Deploy to Render

This repository includes a Render Blueprint (`render.yaml`) that deploys the React UI and FastAPI API together as one Docker web service. The UI calls the API on the same origin, so no separate frontend service or CORS configuration is needed.

1. Push the repository to GitHub and create a new **Blueprint** in Render, then connect the repository.
2. When prompted, provide `GOOGLE_API_KEY` and `PINECONE_API_KEY`. The Blueprint sets the other environment variables; update `PINECONE_INDEX_NAME`, `PINECONE_NAMESPACE`, and the model settings if your Pinecone index or models use different values.
3. Wait for the Docker build and health check to complete, then open the service's `onrender.com` URL. The API docs are at `/docs`.

Create a Pinecone index compatible with the configured embedding model before uploading documents. The Blueprint uses Render's free web-service plan: the service may spin down when idle, and its local filesystem is temporary. Pinecone stores the indexed vectors, but original uploaded PDFs in `DOCUMENTS_DIR` do not survive restarts or redeploys. Use a paid Render plan with a persistent disk and set `DOCUMENTS_DIR` to a directory on that disk if the original files must be retained.

## GitHub Actions

The UI and RAG pipelines run independently when their respective paths change, on pull requests, and by manual dispatch. Pull requests test/build the images without publishing; pushes to the repository's default branch publish `docker.io/<namespace>/enterprise-rag-ui` and `docker.io/<namespace>/enterprise-rag-api` with `latest` and commit-SHA tags. Configure the `DOCKERHUB_NAMESPACE` Actions variable and the `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` Actions secrets. Create a Docker Hub access token with write permission for the target namespace.

To deploy with Compose using published images, set `UI_IMAGE` and `RAG_IMAGE` to the Docker Hub image references (for example, `docker.io/<namespace>/enterprise-rag-ui:latest` and `docker.io/<namespace>/enterprise-rag-api:latest`), then run `docker compose pull` and `docker compose up -d --no-build`. Without those variables, Compose builds and runs local images.

## Modules
- `ingestion/`: loading and chunking
- `models/`: chat and embedding providers
- `retrieval/`: Pinecone vector indexing and search
- `rag/`: reusable retrieval/generation LangGraph subgraph
- `workflows/`: application-level orchestration
- `api/`: upload, chat, and HTTP endpoints
- `web/`: React PDF upload and chat interface
- `security/`: document authorization extension point
- `observability/`: structured logging

## Production checklist
This is a scaffold, not a production-certified deployment. Before production, implement authentication and document-level ACL/tenant filters inside retrieval, managed secrets, rate limits, prompt-injection defenses, evaluation, tracing/metrics/alerts, load tests, and durable graph checkpointing if needed. CLI ingestion replaces all vectors in the configured Pinecone namespace; browser uploads append to that namespace.
