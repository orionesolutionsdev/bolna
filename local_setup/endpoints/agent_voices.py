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
    Voice(provider="deepgram", name="Asteria", model="aura-asteria-en", id="asteria-voice-id", languageCode="en-US", accent="american", gender="female", lowLatency=False),
    Voice(provider="deepgram", name="Luna", model="aura-luna-en", id="luna-voice-id", languageCode="en-US", accent="american", gender="female", lowLatency=False),
    Voice(provider="deepgram", name="Stella", model="aura-stella-en", id="stella-voice-id", languageCode="en-US", accent="american", gender="female", lowLatency=False),
    Voice(provider="deepgram", name="Athena", model="aura-athena-en", id="athena-voice-id", languageCode="en-UK", accent="british", gender="female", lowLatency=False),
    Voice(provider="deepgram", name="Hera", model="aura-hera-en", id="hera-voice-id", languageCode="en-US", accent="american", gender="female", lowLatency=False),
    Voice(provider="deepgram", name="Orion", model="aura-orion-en", id="orion-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False),
    Voice(provider="deepgram", name="Arcas", model="aura-arcas-en", id="arcas-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False),
    Voice(provider="deepgram", name="Perseus", model="aura-perseus-en", id="perseus-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False),
    Voice(provider="deepgram", name="Angus", model="aura-angus-en", id="angus-voice-id", languageCode="en-IE", accent="irish", gender="male", lowLatency=False),
    Voice(provider="deepgram", name="Orpheus", model="aura-orpheus-en", id="orpheus-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False),
    Voice(provider="deepgram", name="Helios", model="aura-helios-en", id="helios-voice-id", languageCode="en-UK", accent="british", gender="male", lowLatency=False),
    Voice(provider="deepgram", name="Zeus", model="aura-zeus-en", id="zeus-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False),
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




