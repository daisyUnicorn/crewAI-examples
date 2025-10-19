from typing import Any
from langchain.tools import tool
from .runtime import AgentBayRuntime


_runtime = AgentBayRuntime()


class AgentBayTools:
    @tool("Run AgentBay task")
    def run_agentbay(input_text: str) -> str:
        """
        调用 AgentBay 运行环境。输入应为 JSON 字符串，包含字段：
        - action: 要执行的动作，如 "retrieve_summarize"
        - inputs: 动作输入，如 {"query": "产品关键词"}
        - config: 运行配置，如 {"top_k": 3}
        返回字符串化的 JSON 结果。
        """
        result = _runtime.run(input_text)
        # 始终返回字符串，确保工具返回可被 LLM 解析
        import json
        return json.dumps(result, ensure_ascii=False)
