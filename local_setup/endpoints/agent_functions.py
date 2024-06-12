import os
import asyncio
import uuid
import traceback
from fastapi import  WebSocket, WebSocketDisconnect, HTTPException, Query, APIRouter, Request
from datetime import datetime
from bolna.helpers.utils import store_file
from bolna.prompts import *
from bolna.helpers.logger_config import configure_logger
from bolna.models import *
from bolna.llms import LiteLLM
import redis
from fastapi.responses import JSONResponse
from vo_utils.clerk_auth_utils import get_user_id_from_Token
from vo_utils.database_utils import db
from dotenv import load_dotenv
router = APIRouter()
load_dotenv()
logger = configure_logger(__name__)
active_websockets: List[WebSocket] = []

from config import settings
from bolna.agent_manager.assistant_manager import AssistantManager
AGENT_WELCOME_MESSAGE = "This call is being recorded for quality assurance and training. Please speak now."

class AgentModel(BaseModel):
    agent_name: str
    agent_type: str = "other"
    tasks: List[Task]
    agent_welcome_message: Optional[str] = AGENT_WELCOME_MESSAGE


class AgentModelPrompt(BaseModel):
    agent_name: str
    agent_type: str = "other"
    tasks: List[Task]
    agent_welcome_message: Optional[str] = AGENT_WELCOME_MESSAGE
    agent_prompts: Optional[Dict[str, Dict[str, str]]] = None
 # Usually of the format task_1: { "system_prompt" : "helpful agent" } #For IVR type it should be a basic graph

class CreateAgentPayload(BaseModel):
    agent_config: AgentModel
    agent_prompts: Optional[Dict[str, Dict[str, str]]]


@router.post("/agent")
async def create_agent(agent_data: CreateAgentPayload, header:Request):
    agent_uuid = str(uuid.uuid4())
    user_id = get_user_id_from_Token(header)
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
    asyncio.gather(
        # redis_client.set(agent_uuid, json.dumps(data_for_db)),
        store_file(file_key=stored_prompt_file_path, file_data=agent_prompts, local=True)
    )
    data_for_db['created_at'] = datetime.now().isoformat()
    data_for_db['agent_id'] = agent_uuid
    data_for_db['agent_prompts'] = agent_prompts
    data_for_db['user_id'] = user_id
    db[settings.MONGO_COLLECTION].insert_one(data_for_db)

    return {"agent_id": agent_uuid, "state": "created"}



@router.get("/agent/all")
async def get_all_agents(header:Request):
    agents_data = []
    user_id = get_user_id_from_Token(header)
    results = list(db[settings.MONGO_COLLECTION].find({"user_id": user_id}, {'_id':0}).sort('created_at', -1))
    for agent in results:
        agent_id = agent.pop('agent_id')
        agents_data.append({'agent_id': agent_id, 'agent_config': agent})
    return JSONResponse(content= agents_data, status_code=200)


@router.get("/agent/{agent_id}")
async def get_agent(agent_id: str, header:Request):
    try:
        user_id = get_user_id_from_Token(header)
        agent_data = db[settings.MONGO_COLLECTION].find_one({"agent_id": agent_id,
                                                             "user_id": user_id},
                                                             {'_id':0, 'agent_id':0})
        if agent_data:
            return JSONResponse(content=agent_data, status_code=200)
        else:
            return JSONResponse(content={"message": "Agent not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)



@router.put("/agent/{agent_id}")
async def update_agent(agent_id: str, agent_data: AgentModelPrompt, header:Request):
    try:
        user_id = get_user_id_from_Token(header)
        agent_config = db[settings.MONGO_COLLECTION].find_one({"agent_id": agent_id,
                                                               "user_id": user_id
                                                               })
        if agent_config:
            agent_data_response = agent_data.model_dump()
            agent_config.update({key: value for key, value in agent_data_response.items()})
            agent_prompts = agent_data_response.get("agent_prompts")
            stored_prompt_file_path = f"{agent_id}/conversation_details.json"
            asyncio.gather(
                store_file(file_key=stored_prompt_file_path, file_data=agent_prompts, local=True)
            )
            db[settings.MONGO_COLLECTION].update_one({"agent_id": agent_id}, {"$set": agent_config})
            return JSONResponse(content={"message": "Agent updated successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Agent not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@router.delete("/agent/{agent_id}")
async def delete_agent(agent_id: str, header:Request):
    try:
        user_id = get_user_id_from_Token(header)
        result = db[settings.MONGO_COLLECTION].delete_one({"agent_id": agent_id, 'user_id': user_id})
        if result.deleted_count == 1:
            return JSONResponse(content={"message": "Agent deleted successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Agent not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)



# app.add_middleware(CustomAuthMiddleware)
active_websockets: List[WebSocket] = []

############################################################################################# 
# Websocket 
#############################################################################################
@router.websocket("/chat/v1/{agent_id}/{context_id}")
async def websocket_endpoint(agent_id: str, websocket: WebSocket, user_agent: str = Query(None)
                             , context_id:  str= ''
                             ):
    logger.info("Connected to ws")
    await websocket.accept()
    active_websockets.append(websocket)
    agent_config, context_data = None, None
    try:
        agent_config = db[settings.MONGO_COLLECTION].find_one({"agent_id": agent_id}, {'_id':0, 'agent_id':0})
        if len(context_id)>0:
            context_data = db[settings.CALL_CONTEXTS].find_one({"context_id": context_id}, 
                                                               {'_id':0, 'context_id':0, 'created_at':0})
        logger.info(f"context_data result: {context_data}")

        if 'agent_welcome_message' in agent_config:
            agent_welcome_message = str(agent_config['agent_welcome_message'])
        else:
            agent_welcome_message = AGENT_WELCOME_MESSAGE
        logger.info(
            f"Retrieved agent config: {agent_config}")
        # agent_config = json.loads(retrieved_agent_config)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=404, detail="Agent not found")
    assistant_manager = AssistantManager(agent_config, websocket, agent_id, agent_welcome_message=agent_welcome_message, context_data=context_data)

    try:
        async for index, task_output in assistant_manager.run(local=True):
            logger.info(task_output)
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"error in executing {e}")




################################################################
# Redis Based Implementation for Agents
from vo_utils.database_utils import db