import os

from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()  # Load .env file

class Settings(BaseSettings):
    # Same secret key as auth server for HS256
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Auth server settings
    AUTH_SERVER_URL: str = "http://localhost:8000"  # Auth server URL
    EXPECTED_ISSUER: str = "auth-service"
    EXPECTED_AUDIENCE: str = "api-service"

@lru_cache()
def get_settings():
    return Settings()