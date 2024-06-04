from fastapi.responses import JSONResponse
from fastapi import  Request, APIRouter
from vo_utils.clerk_auth_utils import get_user_id_from_Token
from config import settings
from vo_utils.database_utils import db




router = APIRouter()
@router.get("/agent/{agent_id}/executions")
async def get_agent(agent_id: str, header:Request):
    try:
        # user_id = get_user_id_from_Token(header)
        if user_id:
            agent_data = db[settings.EXECUTION_COLLECTION].find({"agent_id": agent_id}, {'_id':0})
            if agent_data:
                return JSONResponse(content=list(agent_data), status_code=200)
            else:
                return JSONResponse(content={"message": "Agent not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)



@router.get("/agent/executions/{run_id}")
async def get_agent(run_id: str, header:Request):
    try:
        # user_id = get_user_id_from_Token(header)
        if user_id:
            agent_data = db[settings.EXECUTION_COLLECTION].find_one({"run_id": run_id}, {'_id':0})
            if agent_data:
                return JSONResponse(content=agent_data, status_code=200)
            else:
                return JSONResponse(content={"message": "Run ID not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
