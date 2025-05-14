from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, WebsiteSearchTool

from utils.MyLLM import MyLLM


@CrewBase
class ResearchStores():
    """Pesquisa Lojas de Afiliação - Crew"""

    agent_config = 'config/agents.yaml'
    task_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agent_config['researcher'],
            verbose=True,
            tools=[SerperDevTool(), WebsiteSearchTool()],
            llm=MyLLM.GTP4o_mini,
            allow_delegation=False,
        )

    @agent
    def curator(self) -> Agent:
        return Agent(
            config=self.agent_config['curator'],
            verbose=True,
            llm=MyLLM.GTP4o_mini,
            allow_delegation=False,
        )


    @task
    def research(self) -> Task:
        return Task(
            config=self.task_config['research']
        )

    def selection(self) -> Task:
        return Task(
            config=self.task_config['selection']
        )
    
    @crew
    def store_selection_crew(self) -> Crew:
        return Crew(
            # Define a crew para realização das tarefas
            agents=[
                self.researcher_agent, 
                self.curator_agent
            ],
            tasks=[
                self.research_task, 
                self.selection_task
            ],
            process=Process.sequential,
        )
