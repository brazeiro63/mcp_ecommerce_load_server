from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, WebsiteSearchTool

from tools.db_tools import insert_affiliate_stores_tool, insert_products_tool
from utils.MyLLM import MyLLM


@CrewBase
class ResearchStores():
    """Pesquisa Lojas de Afiliação - Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            tools=[SerperDevTool(), WebsiteSearchTool()],  # type: ignore[index]
            llm=MyLLM.GTP4o_mini,
            allow_delegation=False,
        )

    @agent
    def curator(self) -> Agent:
        return Agent(
            config=self.agents_config['curator'],  # type: ignore[index]
            verbose=True,
            tools=[insert_affiliate_stores_tool, insert_products_tool],
            llm=MyLLM.GTP4o_mini,
            allow_delegation=False,
        )


    @task
    def research(self) -> Task:
        return Task(
            config=self.tasks_config['research']  # type: ignore[index]
        )

    def selection(self) -> Task:
        return Task(
            config=self.tasks_config['selection']  # type: ignore[index]
        )
    
    @crew
    def store_selection_crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
