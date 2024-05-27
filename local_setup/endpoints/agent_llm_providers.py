from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LLMModel(BaseModel):
    library: str
    languages: str
    provider: str
    deprecated: bool
    base_url: Optional[str] = None
    json_mode: str
    model: str
    display_name: str
    family: str
# Initial LLM models data with updated base_url and provider for non-openai models
llm_models = [
    LLMModel(library="openai", languages="en", provider="groq", deprecated=False, base_url="https://api.groq.com/openai/v1", json_mode="no", model="groq/meta-llama/Meta-Llama-3-70B-Instruct", display_name="Meta Llama 3 70B instruct", family="llama"),
    LLMModel(library="openai", languages="en", provider="groq", deprecated=False, base_url="https://api.groq.com/openai/v1", json_mode="no", model="groq/microsoft/WizardLM-2-8x22B", display_name="Wizard LM 8x22B", family="mistral"),
    LLMModel(library="openai", languages="en", provider="groq", deprecated=False, base_url="https://api.groq.com/openai/v1", json_mode="no", model="groq/databricks/dbrx-instruct", display_name="DBRX", family="mistral"),
    LLMModel(library="openai", languages="en", provider="groq", deprecated=False, base_url="https://api.groq.com/openai/v1", json_mode="no", model="groq/mistralai/Mixtral-8x22B-Instruct-v0.1", display_name="Mixtral 8x22B", family="mistral"),
    LLMModel(library="openai", languages="en", provider="groq", deprecated=False, base_url="https://api.groq.com/openai/v1", json_mode="no", model="groq/meta-llama/Meta-Llama-3-8B-Instruct", display_name="Meta Llama 3 8B instruct", family="llama"),
    LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, base_url="https://api.groq.com/openai/v1", json_mode="no", model="groq/HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1", display_name="HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1 [Mixtral 8x22 finetune]", family="mixtral"),
    LLMModel(library="openai", languages="en", provider="groq", deprecated=False, base_url="https://api.groq.com/openai/v1", json_mode="no", model="groq/hermes-2-pro-mistral-7b", display_name="Hermes 2 Mistral", family="mistral"),
    LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, json_mode="No", model="groq/HuggingFaceH4/zephyr-7b-beta", display_name="zephyr-7b-beta", family="zephyr"),
    LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, base_url="https://api.groq.com/openai/v1", json_mode="No", model="groq/gemma-7b-it", display_name="gemma-7b", family="gemma"),
    LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, json_mode="No", model="groq/meta-llama/Llama-2-7b-chat-hf", display_name="Llama-2-7b-chat", family="llama"),
    LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, json_mode="No", model="groq/meta-llama/Llama-2-13b-chat-hf", display_name="Llama-2-13b-chat", family="llama"),
    LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, json_mode="No", model="groq/llama-2-70b-chat", display_name="llama-2-70b-chat", family="llama"),
    LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, json_mode="No", model="groq/Open-Orca/Mistral-7B-OpenOrca", display_name="Mistral-7B-OpenOrca", family="mistral"),
    LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, json_mode="Yes", model="groq/mixtral-8x7b-instruct", display_name="mixtral-8x7b-instruct (Perplexity)", family="mistral"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="Yes", model="gpt-3.5-turbo-1106", display_name="gpt-3.5-turbo-1106", family="openai"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="No", model="gpt-3.5-turbo", display_name="gpt-3.5-turbo", family="openai"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="No", model="gpt-4o", display_name="gpt-4o", family="openai"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="No", model="gpt-4", display_name="gpt-4", family="openai"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="No", model="gpt-4-32k", display_name="gpt-4-32k", family="openai"),
    LLMModel(library="openai", languages="en,hi,gu,fr,it,es", provider="openai", deprecated=False, json_mode="Yes", model="gpt-4-1106-preview", display_name="gpt-4-1106-preview", family="openai"),
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