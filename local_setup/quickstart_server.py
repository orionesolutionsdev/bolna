from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from vo_utils.clerk_auth_utils import CustomAuthMiddleware
from endpoints import voagent_functions, voagent_llm_providers, voagent_voices
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

for endpoint in  [ voagent_functions, voagent_llm_providers, voagent_voices ]:
    app.include_router(endpoint.router)
