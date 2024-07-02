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
    audio: str
    gender: str
    lowLatency: bool

# Initial voices data
voices = [
    Voice(provider="deepgram", audio="/assets/Asteria-rY7gFvhj.wav", name="Asteria", model="aura-asteria-en", id="asteria-voice-id", languageCode="en-US", accent="american", gender="female", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Luna-DCeoeimX.wav", name="Luna", model="aura-luna-en", id="luna-voice-id", languageCode="en-US", accent="american", gender="female", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Stella-CFXkrlQi.wav", name="Stella", model="aura-stella-en", id="stella-voice-id", languageCode="en-US", accent="american", gender="female", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Athena-C6a_6S3K.wav", name="Athena", model="aura-athena-en", id="athena-voice-id", languageCode="en-UK", accent="british", gender="female", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Hera-Ck3-0iA9.wav", name="Hera", model="aura-hera-en", id="hera-voice-id", languageCode="en-US", accent="american", gender="female", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Orion-Ck3-0iA9.wav", name="Orion", model="aura-orion-en", id="orion-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Arcas-u3w4z1vR.mp3", name="Arcas", model="aura-arcas-en", id="arcas-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Perseus-Ck3-0iA9.wav", name="Perseus", model="aura-perseus-en", id="perseus-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Angus-Ck3-0iA9.wav", name="Angus", model="aura-angus-en", id="angus-voice-id", languageCode="en-IE", accent="irish", gender="male", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Orpheus-Ck3-0iA9.wav", name="Orpheus", model="aura-orpheus-en", id="orpheus-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Helios-Ck3-0iA9.wav", name="Helios", model="aura-helios-en", id="helios-voice-id", languageCode="en-UK", accent="british", gender="male", lowLatency=False),
    Voice(provider="deepgram", audio="/assets/Angus-Ck3-0iA9.wav", name="Zeus", model="aura-zeus-en", id="zeus-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False),
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




