FROM python:3.12-slim AS development

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts

RUN python -m pip install --no-cache-dir -e ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "infrastructure.bootstrap:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--no-access-log"]

FROM python:3.12-slim AS production-builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/opt/venv/bin:$PATH

WORKDIR /build

RUN python -m venv /opt/venv

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir .

FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/opt/venv/bin:$PATH

WORKDIR /app

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app \
    && chown app:app /app

COPY --from=production-builder /opt/venv /opt/venv

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ["python", "-c", "import json, os, urllib.request; port = os.environ.get('MCP_SECRET_MANAGER_REST_PORT', '8000'); payload = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/v1/health', timeout=3)); raise SystemExit(0 if payload.get('status') == 'ok' else 1)"]

CMD ["uvicorn", "infrastructure.bootstrap:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
