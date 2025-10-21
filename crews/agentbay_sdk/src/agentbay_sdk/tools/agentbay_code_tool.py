from typing import Optional, Dict, Type
from crewai.tools import BaseTool
from pydantic import Field
from .tool_schema import AgentBayRunCodeInput
from ..api.wuying_agentbay_wrapper import AgentBayCodeExecutor


_executor: Optional[AgentBayCodeExecutor] = None


def _get_executor() -> AgentBayCodeExecutor:
    global _executor
    if _executor is None:
        _executor = AgentBayCodeExecutor()
    return _executor


class AgentBayRunCodeTool(BaseTool):
    name: str = "agentbay_run_code"
    description: str = (
        "Execute code (python/javascript) in AgentBay cloud session and return stdout text. "
        "Input should include: code (the code to execute), language (python or javascript, default: python), "
        "timeout_s (execution timeout in seconds, default: 60), and optional labels (dict)."
    )
    args_schema: Type[AgentBayRunCodeInput] = AgentBayRunCodeInput

    def _run(
        self,
        code: str,
        language: str = "python",
        timeout_s: int = 60,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        """Execute code in AgentBay cloud session."""
        executor = _get_executor()
        return executor.run_code(
            code=code,
            language=language,
            timeout_s=timeout_s,
            labels=labels,
        )


# Create a singleton instance
agentbay_run_code = AgentBayRunCodeTool()

