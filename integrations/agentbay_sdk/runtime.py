import json
import os
from typing import Any, Dict, Optional

try:
    # 假设 SDK 提供如下入口；根据真实 SDK 调整
    from wuying_agentbay_sdk import AgentBayClient  # type: ignore
except Exception:  # 兼容 SDK 未安装阶段
    AgentBayClient = None  # type: ignore


class AgentBayRuntime:
    """
    面向 CrewAI 工具的 AgentBay 运行环境封装。

    该类最小职责：
    - 初始化 AgentBay 客户端（本地/远程）
    - 提供 run 接口：接收字典或 JSON 字符串，返回字典
    """

    def __init__(self, api_base: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.api_base = api_base or os.getenv("AGENTBAY_API_BASE", "")
        self.api_key = api_key or os.getenv("AGENTBAY_API_KEY", "")
        self._client = self._create_client()

    def _create_client(self) -> Any:
        if AgentBayClient is None:
            # 延迟失败：在调用时检查
            return None
        return AgentBayClient(base_url=self.api_base, api_key=self.api_key)

    def run(self, payload: Any) -> Dict[str, Any]:
        """
        统一执行入口。
        期望 payload: Dict 或 JSON 字符串，可包含：
        - action: 要在 AgentBay 中执行的动作，如 "retrieve_summarize"
        - query / inputs: 任务输入
        - config: 运行配置（如工具开关、超时等）
        """
        if isinstance(payload, str):
            try:
                payload_dict = json.loads(payload)
            except json.JSONDecodeError:
                raise ValueError("AgentBayRuntime.run 期望 JSON 字符串或字典作为输入")
        elif isinstance(payload, dict):
            payload_dict = payload
        else:
            raise ValueError("AgentBayRuntime.run 仅支持 str 或 dict 类型的 payload")

        if self._client is None:
            raise RuntimeError("wuying-agentbay-sdk 未安装或导入失败，请安装依赖后重试")

        action = payload_dict.get("action", "")
        inputs = payload_dict.get("inputs", {})
        config = payload_dict.get("config", {})

        # 根据 action 路由到 SDK。以下为示例逻辑，请按实际 SDK 替换
        if action == "retrieve_summarize":
            query = inputs.get("query", "")
            top_k = int(config.get("top_k", 5))
            # 假设 SDK 有这样的接口：
            result = self._client.retrieve_and_summarize(query=query, top_k=top_k)
            return {"ok": True, "data": result}

        # 默认兜底：直接转发到通用执行接口（若 SDK 提供）
        if hasattr(self._client, "execute"):
            result = self._client.execute(payload_dict)
            return {"ok": True, "data": result}

        raise ValueError(f"未知的 action: {action}")
