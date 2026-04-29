# syntax=docker/dockerfile:1.6
# 3.12: стабильные бинарные колёса torch/transformers при pip install (3.13 на билд-сервере часто падает или OOM).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/root/.cache/huggingface \
    TRANSFORMERS_CACHE=/root/.cache/huggingface

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# CPU-only torch до основных зависимостей: sentence-transformers увидит готовый torch
# и не подтянет CUDA-сборку с PyPI (~2 GB) — режет холодный билд на ~3 минуты.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --index-url https://download.pytorch.org/whl/cpu torch

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
