from typing import List
from bolna.models import Transcriber
from fastapi import APIRouter, HTTPException

router = APIRouter()

class TranscriberRes(Transcriber):
    id: str

# Initial transcribers data
transcribers = [
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-en"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="whisper", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="whisper-en"),
]

@router.get("/transcriber", response_model=List[TranscriberRes])
def get_transcriber():
    return transcribers

@router.get("/transcriber/{transcriber_id}", response_model=TranscriberRes)
def get_transcriber(transcriber_id: str):
    transcriber = next((transcriber for transcriber in transcribers if transcriber.id == transcriber_id), None)
    if transcriber is None:
        raise HTTPException(status_code=404, detail="Transcriber not found")
    return transcriber




