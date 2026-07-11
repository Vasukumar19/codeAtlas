import os
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

class SettingsSchema(BaseModel):
    embedding_provider: str
    github_token: str | None = None
    gemini_api_key: str | None = None
    openai_api_key: str | None = None

@router.get("")
async def get_app_settings():
    return {
        "embedding_provider": settings.embedding_provider,
        "github_token": settings.github_token,
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "openai_api_key": os.getenv("OPENAI_API_KEY")
    }

@router.post("")
async def update_app_settings(payload: SettingsSchema):
    # 1. Update in-memory settings
    settings.embedding_provider = payload.embedding_provider
    settings.github_token = payload.github_token
    
    # 2. Update environment variables
    if payload.gemini_api_key is not None:
        os.environ["GEMINI_API_KEY"] = payload.gemini_api_key
    if payload.openai_api_key is not None:
        os.environ["OPENAI_API_KEY"] = payload.openai_api_key
        
    # 3. Write back to .env file
    env_path = Path(__file__).resolve().parents[4] / ".env"
    lines = []
    
    # Read existing env file if present
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if "=" in line_str and not line_str.startswith("#"):
                    k, v = line_str.split("=", 1)
                    k = k.strip()
                    if k in ["EMBEDDING_PROVIDER", "GITHUB_TOKEN", "GEMINI_API_KEY", "OPENAI_API_KEY"]:
                        continue
                lines.append(line)
                
    # Append/add updated settings
    lines.append(f"EMBEDDING_PROVIDER={payload.embedding_provider}\n")
    if payload.github_token:
        lines.append(f"GITHUB_TOKEN={payload.github_token}\n")
    if payload.gemini_api_key:
        lines.append(f"GEMINI_API_KEY={payload.gemini_api_key}\n")
    if payload.openai_api_key:
        lines.append(f"OPENAI_API_KEY={payload.openai_api_key}\n")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
    return {"status": "success"}
