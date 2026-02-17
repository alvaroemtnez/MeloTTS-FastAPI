import os
import tempfile
import traceback
import torch
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from melo.api import TTS

app = FastAPI(
    title="MeloTTS FastAPI",
    description="An OpenAI-compatible API for MeloTTS.",
    version="1.0.0",
)

# Mapping of OpenAI-style voice names to MeloTTS language codes
VOICE_TO_LANG = {
    'EN-Default': 'EN',
    'EN-US': 'EN',
    'EN-BR': 'EN',
    'EN_INDIA': 'EN',
    'EN-AU': 'EN',
    'ES': 'ES',
    'FR': 'FR',
    'ZH': 'ZH',
    'JP': 'JP',
    'KR': 'KR'
}

# --- Config ---
device = os.getenv("MELOTTS_DEVICE", "auto").lower()
if device == "auto":
    device = "cuda" if torch.cuda.is_available() else "cpu"
elif device == "gpu":
    device = "cuda"

models_env = os.getenv("MELOTTS_MODELS", "all").upper()
if models_env == "ALL":
    models_to_load = set(VOICE_TO_LANG.values())
else:
    models_to_load = {lang.strip() for lang in models_env.split(",")}

valid_langs = set(VOICE_TO_LANG.values())
models_to_load = models_to_load.intersection(valid_langs)

# --- Model Loading ---
models = {}
for lang in models_to_load:
    try:
        print(f"Loading [{lang}] model onto {device}...")
        models[lang] = TTS(language=lang, device=device)
        # eval() is critical for consistent inference behavior
        models[lang].eval() 
        print(f"[{lang}] model loaded successfully.")
    except Exception as e:
        print(f"Error loading [{lang}] model: {e}")

ACTIVE_VOICES = [voice for voice, lang in VOICE_TO_LANG.items() if lang in models]

class SpeechRequest(BaseModel):
    input: str
    voice: str = "EN-US"
    model: str = "melo-tts-multilingual"
    speed: float = 1.0

@app.get("/v1/models")
async def list_models():
    """Helper for OpenAI-compatible clients to discover available voices."""
    return {
        "object": "list",
        "data": [
            {"id": voice, "object": "model", "owned_by": "melo-tts"} 
            for voice in ACTIVE_VOICES
        ]
    }

@app.post("/v1/audio/speech")
async def create_speech(request: SpeechRequest, background_tasks: BackgroundTasks):
    if not request.input:
        raise HTTPException(status_code=400, detail="Input text is required.")

    if request.voice not in VOICE_TO_LANG:
        raise HTTPException(
            status_code=400,
            detail=f"Voice '{request.voice}' not recognized. Available: {ACTIVE_VOICES}"
        )

    lang = VOICE_TO_LANG[request.voice]

    if lang not in models:
        raise HTTPException(
            status_code=400,
            detail=f"Model for language '{lang}' is not loaded in this instance."
        )

    # Create a secure temp file
    fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd) # Close handle so MeloTTS can open/write to it safely

    try:
        active_model = models[lang]
        speaker_ids = active_model.hps.data.spk2id

        # Determine correct speaker key
        try:
            # English models use specific sub-keys (EN-US, etc)
            # Other models usually just use the language code as the key
            speaker_key = request.voice if lang == "EN" else lang
            speaker_id = speaker_ids[speaker_key]
        except KeyError:
            # Fallback to first available speaker if exact match fails
            speaker_id = list(speaker_ids.values())[0]
            print(f"Warning: Speaker key '{speaker_key}' not found. Falling back to default.")

        # Generate Audio
        active_model.tts_to_file(
            request.input,
            speaker_id,
            temp_path,
            speed=request.speed
        )

        # Cleanup after response is sent
        background_tasks.add_task(os.remove, temp_path)

        return FileResponse(
            path=temp_path, 
            media_type="audio/wav", 
            filename="speech.wav"
        )

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Synthesis failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")