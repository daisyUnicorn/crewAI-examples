from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator


class AgentBayRunCodeInput(BaseModel):
    code: str = Field(..., description="Code content to execute")
    language: str = Field("python", description="Programming language, either python or javascript")
    timeout_s: int = Field(60, ge=1, le=60, description="Timeout in seconds, max 60s")
    labels: Optional[Dict[str, str]] = Field(None, description="Optional: session labels")

    @field_validator("language")
    @classmethod
    def _validate_language(cls, v: str) -> str:
        lang = v.lower().strip()
        if lang not in {"python", "javascript"}:
            raise ValueError("language must be either python or javascript")
        return lang

