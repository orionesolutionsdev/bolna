from fastapi.responses import JSONResponse
from fastapi import  Request, APIRouter
from vo_utils.clerk_auth_utils import get_user_id_from_Token
from config import settings
from botocore.exceptions import NoCredentialsError, ClientError
from vo_utils.database_utils import db, s3_client, generate_presigned_url, parse_s3_url



router = APIRouter()
@router.get("/agent/{agent_id}/executions")
async def get_agent(agent_id: str, header:Request):
    result = []
    try:
        agent_data = db[settings.EXECUTION_COLLECTION].find({"agent_id": agent_id}, {'_id':0}).sort('created_at', -1)
        for agent in list(agent_data):
                if agent.get('recording_path'):
                    object_key = parse_s3_url(agent['recording_path'])
                    agent['recording_path'] = generate_presigned_url(s3_client, object_key)
                result.append(agent)
        if result:
            return JSONResponse(content= result, status_code=200)
        else:
            return JSONResponse(content={"message": "Agent not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)



@router.get("/agent/executions/{run_id}")
async def get_agent(run_id: str, header:Request):
    try:
        agent_data = db[settings.EXECUTION_COLLECTION].find_one({"run_id": run_id}, {'_id':0})
        if agent_data.get("recording_path"):
            object_key = parse_s3_url(agent_data['recording_path'])
            agent_data['recording_path'] = generate_presigned_url(s3_client, object_key)
        if agent_data:
            return JSONResponse(content=agent_data, status_code=200)
        else:
            return JSONResponse(content={"message": "Run ID not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
