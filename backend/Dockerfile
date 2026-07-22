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

CMD ["uvicorn", "infrastructure.bootstrap:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
