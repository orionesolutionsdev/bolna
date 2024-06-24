from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from vo_utils.clerk_auth_utils import CustomAuthMiddleware
from endpoints import (
    agent_functions,
    agent_llm_providers,
    agent_voices,
    agent_executions,
    agent_batch_calling
)
from bolna.helpers.logger_config import configure_logger
from bolna.models import *
from vo_utils.database_utils import db
from config import settings
import sentry_sdk

logger = configure_logger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for endpoint in [
    agent_functions,
    agent_llm_providers,
    agent_voices,
    agent_executions,
    # agent_batch_calling
]:
    app.include_router(endpoint.router)

try:
    sentry_sdk.init(
        dsn=settings.SENETRY_URL,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )
    logger.info("Sentry SDK initialized")
except Exception as e:
    logger.info(f"Sentry SDK not initialized due to error {e}")
