from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Define the voice model
class Voice(BaseModel):
    provider: str
    name: str
    model: str
    id: str
    languageCode: str
    accent: str
    lowLatency: bool


# Initial voices data
voices = [
    Voice(provider="elevenlabs", name="Vikram", model="eleven_multilingual_v2", id="elaXKhiKoWZo6xP9iPob", languageCode="all", accent="indian", lowLatency=False),
    Voice(provider="elevenlabs", name="Wendy", model="eleven_multilingual_v2", id="rQLJY7vvMTTC7a3CRh5M", languageCode="all", accent="american", lowLatency=False),
    Voice(provider="elevenlabs", name="Ellie", model="eleven_multilingual_v2", id="4upRWoWGNrknWYN6YMHJ", languageCode="all", accent="american", lowLatency=False),
    Voice(provider="elevenlabs", name="Sheps Rocky", model="eleven_multilingual_v2", id="d5xU2Rwln0n15oHMmaTU", languageCode="all", accent="american", lowLatency=False),
    Voice(provider="elevenlabs", name="Adrianna", model="eleven_multilingual_v2", id="lbdM5yk6tkX9B7bLVf5d", languageCode="all", accent="australian", lowLatency=False),
]

@router.get("/voices", response_model=List[Voice])
def get_voices():
    return voices

@router.get("/voices/{voice_id}", response_model=Voice)
def get_voice(voice_id: str):
    voice = next((voice for voice in voices if voice.id == voice_id), None)
    if voice is None:
        raise HTTPException(status_code=404, detail="Voice not found")
    return voice




