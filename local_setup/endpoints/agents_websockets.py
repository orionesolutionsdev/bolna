from fastapi import  WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi import  WebSocket, APIRouter
from bolna.helpers.logger_config import configure_logger
from bolna.models import *
import traceback
from bolna.agent_manager.assistant_manager import AssistantManager
from config import settings

from vo_utils.database_utils import db
logger = configure_logger(__name__)


router = APIRouter()
active_websockets: List[WebSocket] = []

############################################################################################# 
# Websocket 
#############################################################################################
@router.websocket("/chat/v1/{agent_id}")
async def websocket_endpoint(agent_id: str, websocket: WebSocket, user_agent: str = Query(None)):
    """
    This function is a websocket endpoint that handles incoming connections from clients.

    Parameters:
    - agent_id (str): The unique identifier for the agent.
    - websocket (WebSocket): The WebSocket object representing the client connection.
    - user_agent (str, optional): The user agent string provided by the client. Defaults to None.

    Returns:
    - None: This function does not return a value.

    Raises:
    - HTTPException: If the agent is not found in the database.
    - Exception: If an error occurs during the execution of the websocket.

    """
    logger.info("Connected to ws")
    await websocket.accept()
    active_websockets.append(websocket)
    agent_config, context_data = None, None
    try:
        agent_config = db[settings.MONGO_COLLECTION].find_one({"agent_id": agent_id}, {'_id':0, 'agent_id':0})
        logger.info(
            f"Retrieved agent config: {agent_config}")
        # agent_config = json.loads(retrieved_agent_config)
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

