from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, WebsiteSearchTool
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from store_selection_crew import ResearchStores
from utils.MyLLM import MyLLM
import json

# Carregar variáveis de ambiente
load_dotenv()

# Definir o modelo de linguagem
llm = MyLLM.GTP4o_mini

scraper_tool = SerperDevTool()
scraper_tool.n_results = 20
web_rag_tool = WebsiteSearchTool()


def main():

    researche_stores = ResearchStores()

    country: str = 'Brasil'
    period: str = 'junho de 2024 a maio 2025'
    niche: str = 'produtos infantís'

    inputs = {"country": country, "period": period, "niche": niche }

    result = researche_stores.store_selection_crew().kickoff(inputs=inputs)
    return result


if __name__ == "__main__":
    pesquisa = main()
    print(f'Pesquisa: {pesquisa}')
