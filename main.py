from mcp.server.fastmcp import FastMCP
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, WebsiteSearchTool
from dotenv import load_dotenv
from utils.MyLLM import MyLLM

# Carregar variáveis de ambiente
load_dotenv()

# Definir o modelo de linguagem
llm = MyLLM.GTP4o_mini

scraper_tool = SerperDevTool()
scraper_tool.n_results = 20
web_rag_tool = WebsiteSearchTool()

def main():


    # Definindo os Agentes
    # Defininindo o agente que busca lojas candidatas a afiliação
    researcher_agent = Agent (
        role='Affiliate Market Research Analyst',
        goal='Provide up-to-date affiliate market analysis of best Stores to work with',
        backstory='An expert analyst with a keen eye for affiliate market trends.',
        tools=[scraper_tool, web_rag_tool],
        llm=llm,
        allow_delegation=False,
        verbose=True
    )


    # Definindo agente que faz a curadoria das lojas para escolher as melhores
    curator_agent = Agent(
        role='Market Analyst',
        goal='Nail the best choices to get partnership in affiliate market',
        backstory='A skilled market analyst on treads and forecasting results',
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    # Definindo as Tasks
    # Task de busca de lojas candidatas
    research_task = Task(
        description='Research the best trends in affiliate market in seek of good partner stores',
        agent='researcher_agent',
        expected_output='A plaintext list of the markets best choices for partners in affiliate market.'
    )


    # Task de curadoria de lojas
    selection_task = Task(
        description='A filtered list with the top 5 Stores to work with in affiliate market.',
        agent='curator_agent',
        expected_output='A ordered list of the top 5 companies.'
    )

    # Define a crew para realização das tarefas
    store_selction_crew = Crew(
        agents=[researcher_agent, curator_agent],
        tasks=[research_task, selection_task],
        process=Process.sequential,
    )

    result = store_selction_crew.kickoff(inputs={})

