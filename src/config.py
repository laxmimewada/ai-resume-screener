"""
config.py
---------
Central configuration for TalentScout AI.
All settings live here — change one place, affects everything.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Model Configuration
    EMBEDDING_MODEL: str = "models/embedding-001"
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.3
    
    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "4"))
    
    # Storage
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    # Limits
    MAX_FILE_SIZE_MB: int = 10
    MAX_QUESTION_LENGTH: int = 500
    MIN_RESUME_TEXT_LENGTH: int = 50
    
    @property
    def is_api_key_valid(self) -> bool:
        return bool(self.GOOGLE_API_KEY) and self.GOOGLE_API_KEY != "your_api_key_here"


# Single global instance (import this everywhere)
settings = Settings()