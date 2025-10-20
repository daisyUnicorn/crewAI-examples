from typing import Optional, Dict
from langchain.tools import tool
from .tool_schema import AgentBayRunCodeInput
from ..api.wuying_agentbay_wrapper import AgentBayCodeExecutor


_executor: Optional[AgentBayCodeExecutor] = None


def _get_executor() -> AgentBayCodeExecutor:
    global _executor
    if _executor is None:
        _executor = AgentBayCodeExecutor()
    return _executor


@tool("agentbay_run_code", args_schema=AgentBayRunCodeInput)
def agentbay_run_code(
    code: str,
    language: str = "python",
    timeout_s: int = 60,
    labels: Optional[Dict[str, str]] = None,
) -> str:
    """在 AgentBay 云端会话中执行代码（python/javascript），返回 stdout 文本。"""
    executor = _get_executor()
    return executor.run_code(
        code=code,
        language=language,
        timeout_s=timeout_s,
        labels=labels,
    )
