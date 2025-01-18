from typing import Dict, Any
from pydantic_settings import BaseSettings
import json
import os

class Settings(BaseSettings):
    firebase_credentials: Dict[str, Any]
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600  # 1 hour
    request_timeout: int = 30  # seconds

    class Config:
        env_file = ".env"

    @classmethod
    def load(cls) -> "Settings":
        # Load Firebase credentials from environment variable or file
        firebase_creds = os.getenv("FIREBASE_CREDENTIALS")
        if firebase_creds:
            firebase_credentials = json.loads(firebase_creds)
        elif os.path.exists("firebase-credentials.json"):
            with open("firebase-credentials.json", "r") as f:
                firebase_credentials = json.load(f)
        else:
            raise ValueError(
                "Firebase credentials not found. Set FIREBASE_CREDENTIALS env var or provide firebase-credentials.json"
            )
        
        return cls(firebase_credentials=firebase_credentials)

settings = Settings.load()