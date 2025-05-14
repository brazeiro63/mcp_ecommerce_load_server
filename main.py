from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, WebsiteSearchTool
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from store_selection_crew import ResearchStores
from utils.MyLLM import MyLLM

# Carregar variáveis de ambiente
load_dotenv()

# Definir o modelo de linguagem
llm = MyLLM.GTP4o_mini

scraper_tool = SerperDevTool()
scraper_tool.n_results = 20
web_rag_tool = WebsiteSearchTool()


def main():

    result = ResearchStores.store_selection_crew.kickoff(inputs={})
    return result


if __name__ == "__main__":
    main()
