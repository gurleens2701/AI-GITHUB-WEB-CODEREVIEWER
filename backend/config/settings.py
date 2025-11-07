import os
from typing import Optional
from dotenv import load_dotenv

# THIS LINE IS CRITICAL!
load_dotenv()

class Settings:
    """Application settings and configuration."""

    
    def __init__(self):
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.backend_host: str = os.getenv("BACKEND_HOST", "127.0.0.1")
        self.backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
        self.frontend_host: str = os.getenv("FRONTEND_HOST", "0.0.0.0")
        self.frontend_port: int = int(os.getenv("FRONTEND_PORT", "7819"))
        self.model_name: str = os.getenv("MODEL_NAME", "gpt-4")
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.3"))

settings = Settings()
