import os
from typing import Optional, Dict

from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams


class AgentBayCodeExecutor:
    """
    AgentBay SDK 封装：聚焦代码执行场景
    - 负责创建/销毁会话
    - 暴露 run_code 统一接口（支持 python / javascript）
    - 可透传部分创建参数
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AGENTBAY_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "AGENTBAY_API_KEY 未配置，请设置环境变量或在构造函数传入 api_key"
            )
        self._client = AgentBay(api_key=self.api_key)

    def create_session(self, labels: Optional[Dict[str, str]] = None):
        params = CreateSessionParams()
        if labels:
            params.labels = labels
        result = self._client.create(params)
        if not result.success:
            raise RuntimeError(f"创建会话失败: {result.error_message}")
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
            # 清理会话
            self.delete_session(session)
