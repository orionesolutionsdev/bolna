from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LLMModel(BaseModel):
    library: str = "openai"
    languages: str = "en"
    provider: str = "openai"
    deprecated: bool = False
    base_url: Optional[str] = None
    json_mode: str = "Yes"
    model: str = "gpt-3.5-turbo-1106"
    display_name: str = "gpt-3.5-turbo-1106"
    family: str = "openai"

llm_models = [
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="Yes", model="gpt-3.5-turbo-1106", display_name="gpt-3.5-turbo-1106", family="openai"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="No", model="gpt-3.5-turbo", display_name="gpt-3.5-turbo", family="openai"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="No", model="gpt-4o", display_name="gpt-4o", family="openai"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="No", model="gpt-4", display_name="gpt-4", family="openai"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="No", model="gpt-4-32k", display_name="gpt-4-32k", family="openai"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="Yes", model="gpt-4-1106-preview", display_name="gpt-4-1106-preview", family="openai"),
    LLMModel(library="ollama", languages="it", provider="groq", deprecated=False, json_mode="No", model="groq/gemma-7b-it", display_name="gemma-7b-it", family="gemini"),
    LLMModel(library="ollama", languages="en", provider="groq", deprecated=False, json_mode="No", model="groq/llama3-70b-8192", display_name="llama3-70b-8192", family="llama"),
    LLMModel(library="ollama", languages="en", provider="groq", deprecated=False, json_mode="No", model="groq/llama3-8b-8192", display_name="llama3-8b-8192", family="llama"),
    LLMModel(library="ollama", languages="en,fr", provider="groq", deprecated=False, json_mode="No", model="groq/mixtral-8x7b-32768", display_name="mixtral-8x7b-32768", family="mixtral"),
]

@router.get("/llm_models", response_model=List[LLMModel])
def get_llm_models():
    return llm_models


@router.get("/llm_models/{model_name}", response_model=LLMModel)
def get_llm_model(model_name: str):
    model = next((model for model in llm_models if model.model == model_name), None)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return model