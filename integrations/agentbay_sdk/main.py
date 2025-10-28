import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from .tools import AgentBayTools


load_dotenv()

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

researcher = Agent(
    role="产品调研助理",
    goal="基于给定关键词完成检索与结构化要点总结",
    backstory="你擅长调用外部工具完成检索、汇总并生成简报",
    verbose=True,
    tools=[AgentBayTools.run_agentbay],
    llm=llm,
)

research_task = Task(
    description=(
        "针对关键词：'企业级知识库'，调用 AgentBay 工具执行 action=retrieve_summarize，"
        "汇总 3 个关键洞察，输出 Markdown 报告。"
    ),
    expected_output="以 Markdown 形式输出：要点、来源、建议",
    agent=researcher,
)

crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    process=Process.sequential,
)

if __name__ == "__main__":
    crew.kickoff()
