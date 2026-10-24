FROM node:24-alpine AS web-build
WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml README.md uv.lock ./
COPY src ./src
COPY scripts ./scripts
RUN uv sync --frozen --no-dev
COPY --from=web-build /app/web/dist ./web/dist
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn enterprise_rag.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
