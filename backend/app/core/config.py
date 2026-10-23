from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "axiom-observatory"
    version: str = "1.0.0"
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    database_url: str = "sqlite:///./axiom.db"

    # LLM settings
    llm_provider: str = "simulated"
    llm_model: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()