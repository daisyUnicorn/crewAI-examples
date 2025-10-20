from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator


class AgentBayRunCodeInput(BaseModel):
    code: str = Field(..., description="要执行的代码内容")
    language: str = Field("python", description="语言，可选 python/javascript")
    timeout_s: int = Field(60, ge=1, le=60, description="超时时间(秒)，最大 60s")
    labels: Optional[Dict[str, str]] = Field(None, description="可选：会话标签")

    @field_validator("language")
    @classmethod
    def _validate_language(cls, v: str) -> str:
        lang = v.lower().strip()
        if lang not in {"python", "javascript"}:
            raise ValueError("language 必须是 python 或 javascript")
        return lang
