import os
import time
from typing import Optional, Dict

from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams


class AgentBayConnectionError(Exception):
    """AgentBay 连接错误异常"""
    pass


class AgentBayCodeExecutor:
    """
    AgentBay SDK wrapper focusing on code execution scenarios:
    - Manages session creation/deletion
    - Exposes unified run_code interface (supports python/javascript)
    - Allows passthrough of session creation parameters
    - Handles connection errors with retry mechanism
    """

    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, retry_delay: float = 1.0):
        self.api_key = api_key or os.getenv("AGENTBAY_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "AGENTBAY_API_KEY not configured. Please set environment variable or pass api_key to constructor"
            )
        self._client = AgentBay(api_key=self.api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _is_connection_error(self, error: Exception) -> bool:
        """检查是否是连接相关的错误"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        connection_indicators = [
            'connection', 'connect', 'unavailable', 'timeout', 
            'network', 'unreachable', 'refused', 'reset'
        ]
        
        return any(indicator in error_str or indicator in error_type 
                  for indicator in connection_indicators)

    def create_session(self, labels: Optional[Dict[str, str]] = None):
        """创建 AgentBay 会话，带重试机制"""
        params = CreateSessionParams(image_id="code-space-debian-12")
        if labels:
            params.labels = labels
        
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                result = self._client.create(params)
                if not result.success:
                    error_msg = result.error_message or "Unknown error"
                    # 检查是否是连接错误
                    if self._is_connection_error(Exception(error_msg)):
                        if attempt < self.max_retries:
                            wait_time = self.retry_delay * attempt
                            print(f"⚠️  连接错误 (尝试 {attempt}/{self.max_retries}): {error_msg}")
                            print(f"   等待 {wait_time:.1f} 秒后重试...")
                            time.sleep(wait_time)
                            continue
                        else:
                            raise AgentBayConnectionError(
                                f"无法连接到模型提供者。已重试 {self.max_retries} 次。"
                                f"这可能是临时性问题 - 请稍后再试。\n"
                                f"错误详情: {error_msg}"
                            )
                    else:
                        raise RuntimeError(f"创建会话失败: {error_msg}")
                return result.session
            except Exception as e:
                if self._is_connection_error(e):
                    if attempt < self.max_retries:
                        wait_time = self.retry_delay * attempt
                        print(f"⚠️  连接错误 (尝试 {attempt}/{self.max_retries}): {e}")
                        print(f"   等待 {wait_time:.1f} 秒后重试...")
                        time.sleep(wait_time)
                        last_error = e
                        continue
                    else:
                        raise AgentBayConnectionError(
                            f"无法连接到模型提供者。已重试 {self.max_retries} 次。"
                            f"这可能是临时性问题 - 请稍后再试。\n"
                            f"错误详情: {e}"
                        )
                else:
                    raise
        
        if last_error:
            raise AgentBayConnectionError(
                f"无法连接到模型提供者。已重试 {self.max_retries} 次。"
                f"这可能是临时性问题 - 请稍后再试。\n"
                f"最后错误: {last_error}"
            )

    def delete_session(self, session) -> None:
        """删除会话，忽略连接错误"""
        try:
            _ = self._client.delete(session)
        except Exception as e:
            # 删除会话时的错误通常可以忽略
            if not self._is_connection_error(e):
                print(f"警告: 删除会话时出错: {e}")

    def run_code(
        self,
        code: str,
        language: str = "python",
        timeout_s: int = 60,
        labels: Optional[Dict[str, str]] = None,
    ) -> str:
        """执行代码，带连接错误处理"""
        session = None
        try:
            session = self.create_session(labels=labels)
            exec_result = session.code.run_code(code=code, language=language, timeout_s=timeout_s)
            if not exec_result.success:
                error_msg = exec_result.error_message or "执行失败"
                if self._is_connection_error(Exception(error_msg)):
                    raise AgentBayConnectionError(
                        f"执行代码时连接错误: {error_msg}\n"
                        f"这可能是临时性问题 - 请稍后再试。"
                    )
                raise RuntimeError(f"代码执行失败: {error_msg}")
            return exec_result.result
        except AgentBayConnectionError:
            # 重新抛出连接错误
            raise
        except Exception as e:
            if self._is_connection_error(e):
                raise AgentBayConnectionError(
                    f"执行代码时无法连接到模型提供者。\n"
                    f"这可能是临时性问题 - 请稍后再试。\n"
                    f"错误详情: {e}"
                )
            raise
        finally:
            # 清理会话
            if session:
                self.delete_session(session)

