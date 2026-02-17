# --- Stage 1: Builder ---
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04 AS builder

RUN apt-get update && apt-get install -y \
    build-essential python3 python3-pip libmecab-dev git cargo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY . .

RUN pip install --no-cache-dir .

# --- Stage 2: Runtime ---
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip libsndfile1 libmecab2 mecab \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . /app

RUN python3 -m nltk.downloader averaged_perceptron_tagger_eng punkt
RUN python3 -m unidic download
RUN python3 melo/init_downloads.py

EXPOSE 8000
CMD ["uvicorn", "melotts_api:app", "--host", "0.0.0.0", "--port", "8000"]