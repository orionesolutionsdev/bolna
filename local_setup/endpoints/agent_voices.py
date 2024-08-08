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
    engine: Optional[str] = None

# Initial voices data
voices = [
    Voice(provider="azuretts", audio="/assets/Sonia.wav", name="Sonia", model="Neural", id="en-GB-SoniaNeural", languageCode="en-GB", accent="british", gender="female", lowLatency=False),
    Voice(provider="azuretts", audio="/assets/Ryan.wav", name="Ryan", model="Neural", id="en-GB-RyanNeural", languageCode="en-GB", accent="british", gender="male", lowLatency=False),
    Voice(provider="azuretts", audio="/assets/Neerja.wav", name="Neerja", model="Neural", id="en-IN-NeerjaNeural", languageCode="en-IN", accent="indian", gender="female", lowLatency=False),
    Voice(provider="azuretts", audio="/assets/Kavya.wav", name="Kavya", model="Neural", id="hi-IN-KavyaNeural", languageCode="hi-IN", accent="indian", gender="female", lowLatency=False),
    Voice(provider="azuretts", audio="/assets/Kunal.wav", name="Kunal", model="Neural", id="hi-IN-KunalNeural", languageCode="hi-IN", accent="indian", gender="female", lowLatency=False),
    Voice(provider="azuretts", audio="/assets/Ava.wav", name="Ava", model="Neural", id="en-US-AvaNeural", languageCode="en-US", accent="american", gender="female", lowLatency=False),
    Voice(provider="azuretts", audio="/assets/Andrew.wav", name="Andrew", model="Neural", id="en-US-AndrewNeural", languageCode="en-US", accent="american", gender="male", lowLatency=False),
    Voice(provider="polly", audio="/assets/Arthur.mp3", name="Arthur", model="Arthur", id="Arthur", languageCode="en-GB", accent="british", gender="male", lowLatency=False, engine="neural"),
    Voice(provider="polly", audio="/assets/Emma.mp3", name="Emma", model="Emma", id="Emma", languageCode="en-GB", accent="british", gender="female", lowLatency=False, engine="neural"),
    Voice(provider="polly", audio="/assets/Niamh.mp3", name="Niamh", model="Niamh", id="Niamh", languageCode="en-IE", accent="american", gender="female", lowLatency=False, engine="neural"),
    Voice(provider="polly", audio="/assets/Raveena.mp3", name="Raveena", model="Raveena", id="Raveena", languageCode="en-IN", accent="indian", gender="female", lowLatency=False, engine="standard"),
    Voice(provider="polly", audio="/assets/Kajal.mp3", name="Kajal", model="Kajal", id="Kajal", languageCode="hi-IN", accent="indian", gender="female", lowLatency=False, engine="neural"),
    Voice(provider="polly", audio="/assets/Aditi.mp3", name="Aditi", model="Aditi", id="Aditi", languageCode="hi-IN", accent="indian", gender="female", lowLatency=False, engine="standard"),
    Voice(provider="polly", audio="/assets/Joey.mp3", name="Joey", model="Joey", id="Joey", languageCode="en-US", accent="american", gender="male", lowLatency=False, engine="neural"),
    Voice(provider="polly", audio="/assets/Danielle.mp3", name="Danielle", model="Danielle", id="Danielle", languageCode="en-US", accent="american", gender="female", lowLatency=False, engine="neural"),
    Voice(provider="polly", audio="/assets/Raveena_hindi.mp3", name="Raveena", model="Raveena", id="Raveena", languageCode="hi-IN", accent="indian", gender="female", lowLatency=False, engine="standard"),
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
    Voice(provider="deepgram", audio="/assets/Angus-Ck3-0iA9.wav", name="Zeus", model="aura-zeus-en", id="zeus-voice-id", languageCode="en-US", accent="american", gender="male", lowLatency=False)
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
