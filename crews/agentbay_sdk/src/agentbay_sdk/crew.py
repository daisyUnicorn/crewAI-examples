from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from .tools.agentbay_code_tool import agentbay_run_code

load_dotenv()


@CrewBase
class AgentBayCodeCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def code_executor(self) -> Agent:
        return Agent(
            config=self.agents_config['code_executor'],
            tools=[agentbay_run_code],
            allow_delegation=False,
            verbose=True,
        )

    @task
    def run_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['run_code_task'],
            agent=self.code_executor(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
