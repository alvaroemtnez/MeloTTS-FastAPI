FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    python3 \
    python3-pip \
    libmecab-dev \
    mecab \
    curl \
    cargo \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install -e .
RUN python3 -m unidic download
RUN python3 melo/init_downloads.py

EXPOSE 8000
CMD ["uvicorn", "melotts_api:app", "--host", "0.0.0.0", "--port", "8000"]
