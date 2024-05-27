from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from vo_utils.clerk_auth_utils import CustomAuthMiddleware
from endpoints import agent_functions, agent_llm_providers, agent_voices
from bolna.helpers.logger_config import configure_logger
from bolna.models import *
from vo_utils.database_utils import db
logger = configure_logger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

for endpoint in  [ agent_functions, agent_llm_providers, agent_voices ]:
    app.include_router(endpoint.router)
