import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "FaultLine"
    API_V1_STR: str = "/api"
    VERSION: str = "0.1.0"
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    # SQLite Database config
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR / 'faultline.db'}"
    SYNC_DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'faultline.db'}"
    
    # Sandbox configuration
    SANDBOX_BASE_DIR: str = os.getenv("SANDBOX_BASE_DIR", str(Path("/tmp/faultline") if os.name != "nt" else Path(os.environ.get("TEMP", "C:/Temp")) / "faultline"))
    SANDBOX_TIMEOUT_SECONDS: int = 120
    SANDBOX_DEFAULT_CLONE_DEPTH: int = 100
    
    # Security
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    # Gemini API / AI Provider
    GEMINI_API_KEY: str = ""
    DEFAULT_LLM_MODEL: str = "gemini-2.0-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
Path(settings.SANDBOX_BASE_DIR).mkdir(parents=True, exist_ok=True)
