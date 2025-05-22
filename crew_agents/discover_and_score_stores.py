"""
Módulo para descoberta e pontuação de lojas de afiliados.
Utiliza o framework CrewAI para automatizar o processo de pesquisa e avaliação.
"""

import json
import os
from typing import Any, Dict, List

from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, WebsiteSearchTool
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class StoreDiscoveryAgent:
    """
    Classe responsável por descobrir e pontuar lojas de afiliados.
    Utiliza agentes de IA para pesquisar e avaliar as melhores opções.
    """
    
    def __init__(self):
        """Inicializa o agente com as ferramentas necessárias."""
        self.serper_tool = SerperDevTool()
        self.serper_tool.n_results = 20
        self.web_tool = WebsiteSearchTool()
    
    def create_researcher_agent(self, config: Dict[str, Any], llm) -> Agent:
        """
        Cria o agente pesquisador responsável por encontrar lojas de afiliados.
        
        Args:
            config: Configuração do agente
            llm: Modelo de linguagem a ser utilizado
            
        Returns:
            Agent: Agente configurado para pesquisa
        """
        return Agent(
            role=config.get("role", "Affiliate Market Research Analyst"),
            goal=config.get("goal", "Provide up-to-date analysis on the best affiliate market stores"),
            backstory=config.get("backstory", "An expert analyst with a keen eye for affiliate market trends"),
            verbose=True,
            tools=[self.serper_tool, self.web_tool],
            llm=llm,
            allow_delegation=False
        )
    
    def create_curator_agent(self, config: Dict[str, Any], llm) -> Agent:
        """
        Cria o agente curador responsável por filtrar e pontuar as lojas encontradas.
        
        Args:
            config: Configuração do agente
            llm: Modelo de linguagem a ser utilizado
            
        Returns:
            Agent: Agente configurado para curadoria
        """
        return Agent(
            role=config.get("role", "Market Analyst"),
            goal=config.get("goal", "Nail the best choices to get partnership in affiliate market"),
            backstory=config.get("backstory", "A skilled market analyst on treads and forecasting results"),
            verbose=True,
            llm=llm,
            allow_delegation=False
        )
    
    def create_research_task(self, config: Dict[str, Any], agent: Agent) -> Task:
        """
        Cria a tarefa de pesquisa de lojas de afiliados.
        
        Args:
            config: Configuração da tarefa
            agent: Agente responsável pela tarefa
            
        Returns:
            Task: Tarefa configurada
        """
        return Task(
            description=config.get("description", "Research the best trends in affiliate market in seek of good partner stores"),
            expected_output=config.get("expected_output", "A bullet list of the best choices for partners in affiliate market"),
            agent=agent
        )
    
    def create_selection_task(self, config: Dict[str, Any], agent: Agent, context: str = "") -> Task:
        """
        Cria a tarefa de seleção e pontuação das melhores lojas.
        
        Args:
            config: Configuração da tarefa
            agent: Agente responsável pela tarefa
            context: Contexto adicional para a tarefa (resultado da pesquisa)
            
        Returns:
            Task: Tarefa configurada
        """
        return Task(
            description=config.get("description", "A filtered list with the top 5 Stores to work with in affiliate market."),
            expected_output=config.get("expected_output", "A ordered list of the top 5 companies along with store's afiliate program website url."),
            agent=agent,
            context=context
        )
    
    def discover_and_score_stores(self, 
                                 country: str, 
                                 period: str, 
                                 niche: str, 
                                 agents_config: Dict[str, Any],
                                 tasks_config: Dict[str, Any],
                                 llm) -> List[Dict[str, Any]]:
        """
        Executa o processo completo de descoberta e pontuação de lojas.
        
        Args:
            country: País alvo para pesquisa
            period: Período de análise
            niche: Nicho de produtos
            agents_config: Configuração dos agentes
            tasks_config: Configuração das tarefas
            llm: Modelo de linguagem a ser utilizado
            
        Returns:
            List[Dict[str, Any]]: Lista de lojas descobertas e pontuadas
        """
        # Formatar as configurações com os parâmetros fornecidos
        researcher_config = agents_config.get("researcher", {})
        curator_config = agents_config.get("curator", {})
        research_task_config = tasks_config.get("research", {})
        selection_task_config = tasks_config.get("selection", {})
        
        # Substituir placeholders nas configurações
        for config in [researcher_config, curator_config, research_task_config, selection_task_config]:
            for key, value in config.items():
                if isinstance(value, str):
                    config[key] = value.format(country=country, period=period, niche=niche)
        
        # Criar agentes
        researcher = self.create_researcher_agent(researcher_config, llm)
        curator = self.create_curator_agent(curator_config, llm)
        
        # Criar tarefa de pesquisa
        research_task = self.create_research_task(research_task_config, researcher)
        
        # Executar pesquisa
        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True
        )
        
        research_result = crew.kickoff(inputs={"country": country, "period": period, "niche": niche})
        
        # Criar tarefa de seleção com o resultado da pesquisa
        selection_task = self.create_selection_task(selection_task_config, curator, context=research_result)
        
        # Executar seleção
        crew = Crew(
            agents=[curator],
            tasks=[selection_task],
            process=Process.sequential,
            verbose=True
        )
        
        selection_result = crew.kickoff(inputs={"research_result": research_result})
        
        # Processar e formatar o resultado
        try:
            # Tentar extrair uma lista estruturada do resultado
            stores = self._parse_selection_result(selection_result)
        except Exception as e:
            print(f"Erro ao processar resultado: {e}")
            # Retornar o resultado bruto em caso de erro
            stores = [{"name": "Resultado bruto", "url": "", "raw_data": selection_result}]
        
        return stores
    
        
    def _parse_selection_result(self, result) -> List[Dict[str, Any]]:
    def _parse_selection_result(self, result: str) -> List[Dict[str, Any]]:
        """
        Processa o resultado da seleção para extrair informações estruturadas.
        
        Args:
            result: Resultado bruto da seleção (string ou objeto CrewOutput)
            result: Resultado bruto da seleção
            
        Returns:
            List[Dict[str, Any]]: Lista estruturada de lojas
        """
        # Processar o resultado para garantir que temos uma string
        if hasattr(result, 'raw_output'):
            # Se for um objeto CrewOutput
            result_text = str(result.raw_output)
        elif hasattr(result, 'strip'):
            # Se já for uma string
            result_text = result
        else:
            # Caso seja outro tipo
            result_text = str(result)
        
        # Implementação básica - em um cenário real, seria necessário um parser mais robusto
        stores = []
        
        # Tentar extrair informações do texto
        lines = result_text.strip().split('\n')
        lines = result.strip().split('\n')
        current_store = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Verificar se é uma nova loja (começa com número ou marcador de lista)
            if line[0].isdigit() or line.startswith('*') or line.startswith('-'):
                # Salvar loja anterior se existir
                if current_store and 'name' in current_store:
                    stores.append(current_store)
                
                # Iniciar nova loja
                current_store = {"name": line.lstrip('0123456789.*- ').split(':')[0].strip()}
            
            # Extrair URL se presente
            elif 'http' in line:
                url_start = line.find('http' )
                url_start = line.find('http')
                url_end = line.find(' ', url_start) if ' ' in line[url_start:] else len(line)
                current_store['url'] = line[url_start:url_end].strip()
            
            # Adicionar outras informações como descrição
            elif current_store and 'name' in current_store:
                if 'description' not in current_store:
                    current_store['description'] = line
                else:
                    current_store['description'] += " " + line
        
        # Adicionar a última loja se existir
        if current_store and 'name' in current_store:
            stores.append(current_store)
        
        # Se não conseguiu extrair lojas estruturadas, criar uma entrada com o texto completo
        if not stores:
            stores = [{"name": "Resultado não estruturado", "description": str(result_text)}]
        
        return stores




# Função principal para uso direto do módulo
def find_and_score_stores(country: str, period: str, niche: str, llm, agents_config: Dict = None, tasks_config: Dict = None) -> List[Dict[str, Any]]:
    """
    Função principal para descoberta e pontuação de lojas de afiliados.
    
    Args:
        country: País alvo para pesquisa
        period: Período de análise
        niche: Nicho de produtos
        llm: Modelo de linguagem a ser utilizado
        agents_config: Configuração dos agentes (opcional)
        tasks_config: Configuração das tarefas (opcional)
        
    Returns:
        List[Dict[str, Any]]: Lista de lojas descobertas e pontuadas
    """
    agent = StoreDiscoveryAgent()
    
    # Carregar configurações padrão se não fornecidas
    if not agents_config:
        # Tentar carregar do arquivo de configuração
        try:
            import yaml
            with open('config/agents.yaml', 'r') as f:
                agents_config = yaml.safe_load(f)
        except Exception:
            # Usar configuração padrão
            agents_config = {
                "researcher": {
                    "role": "Affiliate Market Research Analyst",
                    "goal": "Provide up-to-date analysis on the best affiliate market stores in {country} for the period {period} to promote products in the {niche} niche.",
                    "backstory": "An expert analyst with a keen eye for affiliate market trends"
                },
                "curator": {
                    "role": "Market Analyst",
                    "goal": "Nail the best choices to get partnership in affiliate market in {country}",
                    "backstory": "A skilled market analyst on treads and forecasting results"
                }
            }
    
    if not tasks_config:
        # Tentar carregar do arquivo de configuração
        try:
            import yaml
            with open('config/tasks.yaml', 'r') as f:
                tasks_config = yaml.safe_load(f)
        except Exception:
            # Usar configuração padrão
            tasks_config = {
                "research": {
                    "description": "Research the best trends in affiliate market in seek of good partner stores",
                    "expected_output": "A bullet list of the best choices for partners in affiliate market, along with statistic data and store's afiliate program website url."
                },
                "selection": {
                    "description": "A filtered list with the top 5 Stores to work with in affiliate market.",
                    "expected_output": "A ordered list of the top 5 companies along with store's afiliate program website url."
                }
            }
    
    return agent.discover_and_score_stores(country, period, niche, agents_config, tasks_config, llm)


# Exemplo de uso
if __name__ == "__main__":
    from utils.MyLLM import MyLLM

    # Exemplo de uso direto
    stores = find_and_score_stores(
        country="Brasil",
        period="junho de 2024 a maio 2025",
        niche="produtos infantis",
        llm=MyLLM.GTP4o_mini
    )
    
    print(json.dumps(stores, indent=2, ensure_ascii=False))
