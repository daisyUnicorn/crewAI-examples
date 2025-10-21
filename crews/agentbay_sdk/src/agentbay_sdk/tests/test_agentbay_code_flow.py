import os
import sys
from pathlib import Path
import pytest
from crewai import Crew

# Allow running tests directly without package installation: add subproject src to sys.path
PROJECT_SRC = Path(__file__).resolve().parents[2]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from agentbay_sdk.crew import AgentBayCodeCrew


@pytest.mark.skipif(
    not os.getenv("AGENTBAY_API_KEY") or not os.getenv("OPENAI_API_KEY"),
    reason="AGENTBAY_API_KEY or OPENAI_API_KEY not set"
)
def test_run_python_code_flow():
    """Start an Agent that uses Tool to execute simple Python code in the cloud.

    This test requires:
    - AGENTBAY_API_KEY: for AgentBay SDK to create sessions
    - OPENAI_API_KEY: for CrewAI Agent to make LLM decisions
    """
    inputs = {
        "code": "print('hello from agentbay')",
        "language": "python",
    }
    crew: Crew = AgentBayCodeCrew().crew()
    result = crew.kickoff(inputs=inputs)
    assert "hello from agentbay" in str(result)

