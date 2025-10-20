import os
import sys
from pathlib import Path
import pytest
from crewai import Crew

# 允许直接运行测试而无需安装包：添加子工程 src 到 sys.path
PROJECT_SRC = Path(__file__).resolve().parents[2]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from agentbay_sdk.crew import AgentBayCodeCrew


@pytest.mark.skipif(not os.getenv("AGENTBAY_API_KEY"), reason="AGENTBAY_API_KEY 未设置")
def test_run_python_code_flow():
    """启动一个 Agent，使用 Tool 在云端执行简单 Python 代码。"""
    inputs = {
        "code": "print('hello from agentbay')",
        "language": "python",
    }
    crew: Crew = AgentBayCodeCrew().crew()
    result = crew.kickoff(inputs=inputs)
    assert "hello from agentbay" in str(result)
