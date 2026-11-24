import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FriendlyEats FastAPI"
    ENVIRONMENT: str = "local"
    FIREBASE_PROJECT_ID: str
    FIREBASE_CREDENTIALS_PATH: str | None = None
    FIRESTORE_EMULATOR_HOST: str | None = None
    FIRESTORE_DATABASE: str = "(default)"
    
    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"), extra="ignore")



settings = Settings()