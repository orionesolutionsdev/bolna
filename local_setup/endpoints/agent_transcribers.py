from typing import List
from bolna.models import Transcriber
from fastapi import APIRouter, HTTPException

router = APIRouter()

class TranscriberRes(Transcriber):
    id: str

# Initial transcribers data
transcribers = [
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-general", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-en-general"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-general", language="hi", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-hi-general"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-meeting", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-meeting"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-phonecall", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-phonecall"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-voicemail", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-voicemail"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-finance", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-finance"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-conversationalai", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-conversationalai"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-video", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-video"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-medical", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-medical"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-drivethru", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-drivethru"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="nova-2-automotive", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="nova-2-automotive"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="whisper-large", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="whisper-large"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="whisper-large", language="hi", encoding="linear16", provider="deepgram", task="transcribe", id="whisper-large-hindi"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="whisper-medium", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="whisper-medium"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="whisper-small", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="whisper-small"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="whisper-base", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="whisper-base"),
    TranscriberRes(sampling_rate=16000, endpointing=400, keywords="", stream=True, model="whisper-tiny", language="en", encoding="linear16", provider="deepgram", task="transcribe", id="whisper-tiny"),
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




