
# MeloTTS-FastAPI

A simple OpenAI-compatible FastAPI wrapper for the [MyShell-AI/MeloTTS](https://github.com/myshell-ai/MeloTTS) text-to-speech engine.

## DISCLAMER

This wrapper was heavily AI generated. It is provided under absolutely no warranty. If you find any unexpected behaviour, I could look into it when I have free time.

---

## Features

* **Multilingual Support:** Supports English (multiple accents), Spanish, French, Chinese, Japanese, and Korean.
* **Configurable via ENV:** Control which models load and which device (CPU/CUDA) to use via Environment Variables.
* **OpenAI-Compatible:** Drop-in compatibility for `/v1/audio/speech`, making it perfect for **Open WebUI**.
* **Memory Efficient:** Only load the languages you actually need to save RAM/VRAM.

---

## Configuration (Environment Variables)

Before running the server, you can configure it using the following variables:

| Variable | Description | Default |
| --- | --- | --- |
| `MELOTTS_DEVICE` | Hardware to use: `cpu`, `cuda`, `cuda:0`, or `auto`. | `cpu` |
| `MELOTTS_MODELS` | Comma-separated list of models to load: `EN,ES,FR,ZH,JP,KR` or `ALL`. | `ALL` |

---

## Running with Docker (Recommended)

The easiest way to deploy the API is using the pre-built Docker image:

**Example: Load only English and Spanish on CPU**

```bash
docker run -p 8000:8000 \
  -e MELOTTS_MODELS="EN,ES" \
  -e MELOTTS_DEVICE="cpu" \
  ghcr.io/alvaroemtnez/melotts-fastapi:latest

```

**Example: Load all languages on GPU**

```bash
docker run --gpus all -p 8000:8000 \
  -e MELOTTS_MODELS="ALL" \
  -e MELOTTS_DEVICE="cuda" \
  ghcr.io/alvaroemtnez/melotts-fastapi:latest

```

---

## 🔌 Connecting to Open WebUI

1. Navigate to **Settings > Audio**.
2. **Text-to-Speech Engine:** OpenAI
3. **OpenAI API Base URL:** `http://localhost:8000/v1`
4. **OpenAI API Key:** Can be set to anything (e.g., `12345`).
5. **Voice:** Choose from `EN-US`, `EN-BR`, `ES`, `FR`, etc. (Note: Only voices for models you loaded will appear in the API list).

---

## 🛠️ API Usage Examples

### List Active Voices

Only shows voices for models currently loaded in memory.

```bash
curl http://localhost:8000/v1/audio/voices

```

### Synthesize French Speech

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  --data '{
    "input": "La lueur dorée du soleil caresse les vagues.",
    "voice": "FR",
    "speed": 1.0
  }' \
  --output test_fr.wav

```

### Synthesize Spanish Speech

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Content-Type: application/json" \
  --data '{
    "input": "Hola, ¿cómo estás hoy?",
    "voice": "ES"
  }' \
  --output test_es.wav

```
---

## 📝 Available Voices Mapping

If you load a model (e.g., `EN`), the following voices become available:

* **EN:** `EN-Default`, `EN-US`, `EN-BR`, `EN_INDIA`, `EN-AU`
* **ES:** `ES`
* **FR:** `FR`
* **ZH:** `ZH`
* **JP:** `JP`
* **KR:** `KR`

## Acknowledgements

This is heavily based on [highfillgoods/MeloTTS-API-Locally](https://github.com/highfillgoods/MeloTTS-API-Locally) but with added languages and a ready to use Docker image. Also, many thanks to the authors of [MyShell-AI/MeloTTS](https://github.com/myshell-ai/MeloTTS):
- [Wenliang Zhao](https://wl-zhao.github.io) at Tsinghua University
- [Xumin Yu](https://yuxumin.github.io) at Tsinghua University
- [Zengyi Qin](https://www.qinzy.tech) (project lead) at MIT and MyShell