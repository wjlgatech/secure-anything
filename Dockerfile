# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN pip install --upgrade pip && pip install ".[redis]"

# Run as non-root (least privilege).
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8099
CMD ["uvicorn", "secure_anything.organs.agentgate.main:app", "--host", "0.0.0.0", "--port", "8099"]
