import os
import asyncio
import uuid
import traceback
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from dotenv import load_dotenv
from bolna.helpers.utils import store_file
from bolna.prompts import *
from bolna.helpers.logger_config import configure_logger
from bolna.models import *
from bolna.llms import LiteLLM
from bolna.agent_manager.assistant_manager import AssistantManager
from fastapi.responses import JSONResponse

load_dotenv()
logger = configure_logger(__name__)

redis_pool = redis.ConnectionPool.from_url(os.getenv('REDIS_URL'), decode_responses=True)
redis_client = redis.Redis.from_pool(redis_pool)
active_websockets: List[WebSocket] = []

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class CreateAgentPayload(BaseModel):
    agent_config: AgentModel
    agent_prompts: Optional[Dict[str, Dict[str, str]]]


@app.post("/agent")
async def create_agent(agent_data: CreateAgentPayload):
    agent_uuid = str(uuid.uuid4())
    data_for_db = agent_data.agent_config.model_dump()
    data_for_db["assistant_status"] = "seeding"
    agent_prompts = agent_data.agent_prompts
    logger.info(f'Data for DB {data_for_db}')

    if len(data_for_db['tasks']) > 0:
        logger.info("Setting up follow up tasks")
        for index, task in enumerate(data_for_db['tasks']):
            if task['task_type'] == "extraction":
                extraction_prompt_llm = os.getenv("EXTRACTION_PROMPT_GENERATION_MODEL")
                extraction_prompt_generation_llm = LiteLLM(model=extraction_prompt_llm, max_tokens=2000)
                extraction_prompt = await extraction_prompt_generation_llm.generate(
                    messages=[
                        {'role': 'system', 'content': EXTRACTION_PROMPT_GENERATION_PROMPT},
                        {'role': 'user', 'content': data_for_db["tasks"][index]['tools_config']["llm_agent"]['extraction_details']}
                    ])
                data_for_db["tasks"][index]["tools_config"]["llm_agent"]['extraction_json'] = extraction_prompt

    stored_prompt_file_path = f"{agent_uuid}/conversation_details.json"
    await asyncio.gather(
        redis_client.set(agent_uuid, json.dumps(data_for_db)),
        store_file(file_key=stored_prompt_file_path, file_data=agent_prompts, local=True)
    )

    return {"agent_id": agent_uuid, "state": "created"}

@app.get("/agent/all")
async def get_all_agents():
    agent_ids = await redis_client.keys()
    agents_data = []
    for agent_id in agent_ids:
        agent_config = await redis_client.get(agent_id)
        if agent_config:
            agent_config = json.loads(agent_config)
            agent_name = agent_config.get("agent_name")
            if agent_name:
                agent_data = {
                    "agent_id": agent_id,
                    "agent_config": agent_config
                }
                agents_data.append(agent_data)
    return JSONResponse(content=agents_data, status_code=200)


@app.get("/agent/{agent_id}")
async def get_agent(agent_id: str):
    try:
        print(redis_client.keys())
        retrieved_agent_config = await redis_client.get(agent_id)
        if retrieved_agent_config:
            agent_config = json.loads(retrieved_agent_config)
            return JSONResponse(content=agent_config, status_code=200)
        else:
            return JSONResponse(content={"message": "Agent not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)



@app.put("/agent/{agent_id}")
async def update_agent(agent_id: str, agent_data: AgentModel):
    try:
        retrieved_agent_config = await redis_client.get(agent_id)
        if retrieved_agent_config:
            agent_config = json.loads(retrieved_agent_config)
            agent_config.update({key: value for key, value in agent_data.model_dump().items()})
            await redis_client.set(agent_id, json.dumps(dict(agent_config)))
            return JSONResponse(content={"message": "Agent updated successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Agent not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)



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
    # Voice(provider="polly", name="Matthew", model="generative", id="Matthew", languageCode="en-US", accent="United States (English) (american)", lowLatency=True),
    # Voice(provider="polly", name="Danielle", model="neural", id="Danielle", languageCode="en-US", accent="United States (English) (american)", lowLatency=True),
    # Voice(provider="polly", name="Gregory", model="neural", id="Gregory", languageCode="en-US", accent="United States (English) (american)", lowLatency=True),
    # Voice(provider="polly", name="Kajal", model="neural", id="Kajal", languageCode="en-IN", accent="Indian", lowLatency=True),
    # Voice(provider="polly", name="Arthur", model="neural", id="Arthur", languageCode="en-GB", accent="British", lowLatency=True),
    # Voice(provider="polly", name="Olivia", model="neural", id="Olivia", languageCode="en-AU", accent="Australian", lowLatency=True),
    Voice(provider="elevenlabs", name="Vikram", model="eleven_multilingual_v2", id="elaXKhiKoWZo6xP9iPob", languageCode="all", accent="indian", lowLatency=False),
    Voice(provider="elevenlabs", name="Wendy", model="eleven_multilingual_v2", id="rQLJY7vvMTTC7a3CRh5M", languageCode="all", accent="american", lowLatency=False),
    Voice(provider="elevenlabs", name="Ellie", model="eleven_multilingual_v2", id="4upRWoWGNrknWYN6YMHJ", languageCode="all", accent="american", lowLatency=False),
    Voice(provider="elevenlabs", name="Sheps Rocky", model="eleven_multilingual_v2", id="d5xU2Rwln0n15oHMmaTU", languageCode="all", accent="american", lowLatency=False),
    Voice(provider="elevenlabs", name="Adrianna", model="eleven_multilingual_v2", id="lbdM5yk6tkX9B7bLVf5d", languageCode="all", accent="australian", lowLatency=False),
]

@app.get("/voices", response_model=List[Voice])
def get_voices():
    return voices

@app.get("/voices/{voice_id}", response_model=Voice)
def get_voice(voice_id: str):
    voice = next((voice for voice in voices if voice.id == voice_id), None)
    if voice is None:
        raise HTTPException(status_code=404, detail="Voice not found")
    return voice



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
    # LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, json_mode="no", model="groq/sonar-medium-chat", display_name="Perplexity Sonar medium", family="perplexity"),
    # LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, json_mode="no", model="groq/sonar-small-chat", display_name="Perplexity Sonar small", family="perplexity"),
    # LLMModel(library="litellm", languages="en", provider="groq", deprecated=False, base_url="https://api.groq.com/openai/v1", json_mode="no", model="groq/cognitivecomputations/dolphin-2.6-mixtral-8x7b", display_name="dolphin-2.6-mixtral-8x7b", family="mixtral"),
    # LLMModel(library="azure", languages="en,hi,gu,fr,it,es", provider="azure", deprecated=False, base_url="https://bolna-openai-call.openai.azure.com", json_mode="no", model="azure/bolna-deployment", display_name="azure-openai", family="azure-openai")
]

@app.get("/llm_models", response_model=List[LLMModel])
def get_llm_models():
    return llm_models


@app.get("/llm_models/{model_name}", response_model=LLMModel)
def get_llm_model(model_name: str):
    model = next((model for model in llm_models if model.model == model_name), None)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

############################################################################################# 
# Websocket 
#############################################################################################
@app.websocket("/chat/v1/{agent_id}")
async def websocket_endpoint(agent_id: str, websocket: WebSocket, user_agent: str = Query(None)):
    logger.info("Connected to ws")
    await websocket.accept()
    active_websockets.append(websocket)
    agent_config, context_data = None, None
    try:
        retrieved_agent_config = await redis_client.get(agent_id)
        logger.info(
            f"Retrieved agent config: {retrieved_agent_config}")
        agent_config = json.loads(retrieved_agent_config)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=404, detail="Agent not found")

    assistant_manager = AssistantManager(agent_config, websocket, agent_id)

    try:
        async for index, task_output in assistant_manager.run(local=True):
            logger.info(task_output)
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"error in executing {e}")
