import os
from typing import Optional, Dict

from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams


class AgentBayCodeExecutor:
    """
    AgentBay SDK wrapper focusing on code execution scenarios:
    - Manages session creation/deletion
    - Exposes unified run_code interface (supports python/javascript)
    - Allows passthrough of session creation parameters
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AGENTBAY_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "AGENTBAY_API_KEY not configured. Please set environment variable or pass api_key to constructor"
            )
        self._client = AgentBay(api_key=self.api_key)

    def create_session(self, labels: Optional[Dict[str, str]] = None):
        params = CreateSessionParams(image_id="code-space-debian-12")
        if labels:
            params.labels = label
        result = self._client.create(params)
        if not result.success:
            raise RuntimeError(f"Failed to create session: {result.error_message}")
        return result.session

    def delete_session(self, session) -> None:
        _ = self._client.delete(session)

    def run_code(
        self,
        code: str,
        language: str = "python",
        timeout_s: int = 60,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        session = self.create_session(labels=labels)
        try:
            exec_result = session.code.run_code(code=code, language=language, timeout_s=timeout_s)
            if not exec_result.success:
                raise RuntimeError(exec_result.error_message)
            return exec_result.result
        finally:
            # Clean up session
            self.delete_session(session)

