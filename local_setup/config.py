from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGODB_URI: str
    MONGO_DATABASE: str
    MONGO_COLLECTION: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    MONGODB_URI : str
    DEEPGRAM_AUTH_TOKEN : str
    DEEPGRAM_API_KEY : str
    # OPEN_API_KEY : str
    OPENAI_API_KEY: str
    ENVIRONMENT : str
    WEBSOCKET_URL :str
    APP_CALLBACK_URL: str
    REDIS_URL: str
    TTS_WS: str
    ELEVENLABS_API_KEY: str
    # LITELLM_MODEL_API_KEY :str
    # LITELLM_MODEL_API_BASE : str
    MONGO_DATABASE: str
    MONGO_COLLECTION : str
    BATCH_COLLECTION : str = "batches"
    CALL_CONTEXTS: str = "call_contexts"
    EXECUTION_COLLECTION : str = "execution_metadata"
    RECORDING_BUCKET_NAME : str = "mybot-development"
    BATCH_COLLECTION: str= "batches"
    CALL_QUEUE: str= "call_queues"
    from_number:str = "+14159928208"
    CALL_URL: str="https://call-twillio.customerdemourl.com/call"
    JWKS_URL: str= "https://civil-marmoset-57.clerk.accounts.dev/.well-known/jwks.json"
    SENETRY_URL: str= 'https://bb616da6737c2a0dcdcf52aacdbcaf37@o4507378311495680.ingest.us.sentry.io/4507378318704640' # test_url
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()




