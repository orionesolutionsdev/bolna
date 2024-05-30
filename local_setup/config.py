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
    OPEN_API_KEY : str
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
    EXECUTION_COLLECTION : str = "execution_met"
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()




