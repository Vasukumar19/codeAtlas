import os
import secrets
from pathlib import Path
from fastapi import APIRouter, Header, HTTPException, status, Depends
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

# Strict admin token dependency for securing configuration settings (constant-time check)
async def verify_admin_token(x_admin_token: str | None = Header(None, alias="X-Admin-Token")):
    expected = os.getenv("ADMIN_API_TOKEN")
    if not expected or not x_admin_token or not secrets.compare_digest(x_admin_token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized settings access"
        )

class SettingsSchema(BaseModel):
    embedding_provider: str
    github_token: str | None = None
    gemini_api_key: str | None = None
    openai_api_key: str | None = None

def mask_key(val: str | None) -> str:
    if not val:
        return ""
    return "••••••••"

def is_safe_value(val: str | None) -> bool:
    if not val:
        return True
    # Forbid control characters, quotes, newlines, and backslashes to prevent .env injection
    forbiddens = ["\n", "\r", '"', "'", "\\", "\0"]
    return not any(f in val for f in forbiddens)

@router.get("", dependencies=[Depends(verify_admin_token)])
async def get_app_settings():
    return {
        "embedding_provider": settings.embedding_provider,
        "github_token": mask_key(settings.github_token),
        "gemini_api_key": mask_key(os.getenv("GEMINI_API_KEY")),
        "openai_api_key": mask_key(os.getenv("OPENAI_API_KEY"))
    }

@router.post("", dependencies=[Depends(verify_admin_token)])
async def update_app_settings(payload: SettingsSchema):
    # 1. Load current values
    current_github = settings.github_token
    current_gemini = os.getenv("GEMINI_API_KEY")
    current_openai = os.getenv("OPENAI_API_KEY")
    
    # 2. Determine updated secrets (keep existing if masked placeholder submitted)
    new_github = current_github if payload.github_token == "••••••••" else (payload.github_token or None)
    new_gemini = current_gemini if payload.gemini_api_key == "••••••••" else (payload.gemini_api_key or None)
    new_openai = current_openai if payload.openai_api_key == "••••••••" else (payload.openai_api_key or None)
    
    # 3. Validate values to prevent env file injection
    for name, val in [("github_token", new_github), ("gemini_api_key", new_gemini), ("openai_api_key", new_openai)]:
        if val is not None and not is_safe_value(val):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid characters in {name} configuration"
            )
            
    # 4. Update memory & env vars
    settings.embedding_provider = payload.embedding_provider
    settings.github_token = new_github
    
    if new_gemini is not None:
        os.environ["GEMINI_API_KEY"] = new_gemini
    else:
        os.environ.pop("GEMINI_API_KEY", None)
        
    if new_openai is not None:
        os.environ["OPENAI_API_KEY"] = new_openai
    else:
        os.environ.pop("OPENAI_API_KEY", None)
        
    # 5. Write back to .env file safely
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
    if new_github:
        lines.append(f"GITHUB_TOKEN={new_github}\n")
    if new_gemini:
        lines.append(f"GEMINI_API_KEY={new_gemini}\n")
    if new_openai:
        lines.append(f"OPENAI_API_KEY={new_openai}\n")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
    return {"status": "success"}
