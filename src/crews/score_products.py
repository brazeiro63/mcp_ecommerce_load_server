"""
Módulo para pontuação e priorização de produtos.
Utiliza o framework CrewAI para automatizar o processo de avaliação e ranqueamento.
"""

import json
import os
from typing import Any, Dict, List

from crewai import Agent, Crew, CrewOutput, Process, Task
from crewai_tools import SerperDevTool, WebsiteSearchTool
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class ProductScoringAgent:
    """
    Classe responsável por pontuar e priorizar produtos.
    Utiliza agentes de IA para avaliar os melhores produtos com base em critérios definidos.
    """
    
    def __init__(self):
        """Inicializa o agente com as ferramentas necessárias."""
        self.serper_tool = SerperDevTool()
        self.web_tool = WebsiteSearchTool()
    
    def create_analyst_agent(self, llm) -> Agent:
        """
        Cria o agente analista responsável por avaliar produtos.
        
        Args:
            llm: Modelo de linguagem a ser utilizado
            
        Returns:
            Agent: Agente configurado para análise
        """
        return Agent(
            role="Product Analysis Expert",
            goal="Evaluate products based on market trends, pricing, and potential profitability",
            backstory="An experienced product analyst with deep knowledge of e-commerce and consumer behavior",
            verbose=True,
            tools=[self.serper_tool, self.web_tool],
            llm=llm,
            allow_delegation=False
        )
    
    def create_curator_agent(self, llm) -> Agent:
        """
        Cria o agente curador responsável por priorizar os produtos analisados.
        
        Args:
            llm: Modelo de linguagem a ser utilizado
            
        Returns:
            Agent: Agente configurado para curadoria
        """
        return Agent(
            role="Product Curator",
            goal="Select and prioritize the most promising products for affiliate marketing",
            backstory="A strategic curator with expertise in identifying high-conversion products",
            verbose=True,
            llm=llm,
            allow_delegation=False
        )
    
    def create_analysis_task(self, agent: Agent, products: List[Dict[str, Any]]) -> Task:
        """
        Cria a tarefa de análise de produtos.
        
        Args:
            agent: Agente responsável pela tarefa
            products: Lista de produtos a serem analisados
            
        Returns:
            Task: Tarefa configurada
        """
        products_str = json.dumps(products, ensure_ascii=False, indent=2)
        
        return Task(
            description=f"""
            Analyze the following products to determine their market potential, pricing competitiveness, 
            and likely conversion rate. Consider current market trends, seasonality, and target audience.
            
            Products:
            {products_str}
            """,
            expected_output="""
            A detailed analysis of each product with the following information:
            1. Market potential score (1-10)
            2. Price competitiveness score (1-10)
            3. Estimated conversion rate (%)
            4. Seasonality factors
            5. Target audience match
            6. Overall score (1-10)
            """,
            agent=agent
        )
    
    def create_curation_task(self, agent: Agent, analysis_result: str) -> Task:
        """
        Cria a tarefa de curadoria e priorização dos produtos analisados.
        """
        return Task(
            description="""
            Based on the product analysis, select and prioritize the top products for affiliate marketing.
            Focus on products with the highest potential for conversion and profitability.
            """,
            expected_output="""
            A prioritized list of products with:
            1. Rank (1 being highest priority)
            2. Product name
            3. Overall score
            4. Key strengths
            5. Recommended marketing approach
            """,
            agent=agent,
            inputs={"analysis_result": analysis_result.raw if isinstance(analysis_result, CrewOutput) else analysis_result}
        )

    def score_products(self, products: List[Dict[str, Any]], llm) -> List[Dict[str, Any]]:
        """
        Executa o processo completo de pontuação e priorização de produtos.
        
        Args:
            products: Lista de produtos a serem avaliados
            llm: Modelo de linguagem a ser utilizado
            
        Returns:
            List[Dict[str, Any]]: Lista de produtos pontuados e priorizados
        """
        # Criar agentes
        analyst = self.create_analyst_agent(llm)
        curator = self.create_curator_agent(llm)
        
        # Criar tarefa de análise
        analysis_task = self.create_analysis_task(analyst, products)
        
        # Executar análise
        analysis_crew = Crew(
            agents=[analyst],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True
        )
        
        analysis_result = analysis_crew.kickoff()
        
        # Criar tarefa de curadoria
        curation_task = self.create_curation_task(curator, analysis_result)
        
        # Executar curadoria
        curation_crew = Crew(
            agents=[curator],
            tasks=[curation_task],
            process=Process.sequential,
            verbose=True
        )
        
        curation_result = curation_crew.kickoff()
        
        # Processar e formatar o resultado
        try:
            # Tentar extrair uma lista estruturada do resultado
            scored_products = self._parse_curation_result(curation_result, products)
        except Exception as e:
            print(f"Erro ao processar resultado: {e}")
            # Retornar os produtos originais com o resultado bruto
            scored_products = products
            for product in scored_products:
                product["raw_score_data"] = curation_result
        
        return scored_products
    
    def _parse_curation_result(self, result: str, original_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa o resultado da curadoria para extrair informações estruturadas.
        
        Args:
            result: Resultado bruto da curadoria
            original_products: Lista original de produtos
            
        Returns:
            List[Dict[str, Any]]: Lista estruturada de produtos pontuados
        """
        # Criar cópia dos produtos originais para adicionar pontuações
        scored_products = []
        product_map = {p.get("title", ""): p for p in original_products}
        
        # Extrair informações do texto
        lines = result.strip().split('\n')
        current_product = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Verificar se é um novo produto (começa com número ou marcador de lista)
            if (line[0].isdigit() and '. ' in line[:10]) or line.startswith('*') or line.startswith('-'):
                # Salvar produto anterior se existir
                if current_product and 'product_name' in current_product:
                    # Encontrar produto original
                    original = product_map.get(current_product['product_name'])
                    if original:
                        # Mesclar dados
                        merged = original.copy()
                        merged.update({
                            "rank": current_product.get('rank', 999),
                            "score": current_product.get('score', 0),
                            "strengths": current_product.get('strengths', ""),
                            "marketing_approach": current_product.get('marketing_approach', "")
                        })
                        scored_products.append(merged)
                
                # Iniciar novo produto
                rank_part = line.split('.')[0].strip() if '.' in line else ""
                name_part = line.split('.')[1].strip() if '.' in line else line.lstrip('*- ')
                
                current_product = {
                    "rank": int(rank_part) if rank_part.isdigit() else 999,
                    "product_name": name_part
                }
            
            # Extrair pontuação
            elif "score" in line.lower() and ":" in line:
                score_text = line.split(":")[-1].strip()
                try:
                    # Extrair número da pontuação
                    import re
                    score_match = re.search(r'(\d+(\.\d+)?)', score_text)
                    if score_match:
                        current_product['score'] = float(score_match.group(1))
                except:
                    current_product['score'] = 0
            
            # Extrair pontos fortes
            elif "strength" in line.lower() and ":" in line:
                current_product['strengths'] = line.split(":")[-1].strip()
            
            # Extrair abordagem de marketing
            elif "marketing" in line.lower() and ":" in line:
                current_product['marketing_approach'] = line.split(":")[-1].strip()
        
        # Adicionar o último produto se existir
        if current_product and 'product_name' in current_product:
            original = product_map.get(current_product['product_name'])
            if original:
                merged = original.copy()
                merged.update({
                    "rank": current_product.get('rank', 999),
                    "score": current_product.get('score', 0),
                    "strengths": current_product.get('strengths', ""),
                    "marketing_approach": current_product.get('marketing_approach', "")
                })
                scored_products.append(merged)
        
        # Ordenar por rank
        scored_products.sort(key=lambda x: x.get('rank', 999))
        
        # Se não conseguiu extrair produtos estruturados, retornar os originais
        if not scored_products:
            for i, product in enumerate(original_products):
                product_copy = product.copy()
                product_copy["raw_score_data"] = result
                product_copy["rank"] = i + 1
                scored_products.append(product_copy)
        
        return scored_products


# Função principal para uso direto do módulo
def score_products(products: List[Dict[str, Any]], llm) -> List[Dict[str, Any]]:
    """
    Função principal para pontuação e priorização de produtos.
    
    Args:
        products: Lista de produtos a serem avaliados
        llm: Modelo de linguagem a ser utilizado
        
    Returns:
        List[Dict[str, Any]]: Lista de produtos pontuados e priorizados
    """
    agent = ProductScoringAgent()
    return agent.score_products(products, llm)


# Exemplo de uso
if __name__ == "__main__":
    from src.utils.MyLLM import MyLLM

    # Produtos de exemplo
    sample_products = [
        {
            "title": "Smartphone XYZ Pro",
            "description": "Smartphone de última geração com câmera de 108MP e tela AMOLED de 6.7 polegadas",
            "price": 2999.90,
            "category": "Eletrônicos",
            "brand": "XYZ",
            "product_url": "https://example.com/products/xyz-pro"
        },
        {
            "title": "Notebook ABC Ultra",
            "description": "Notebook ultrafino com processador Intel i7, 16GB RAM e SSD de 512GB",
            "price": 5499.90,
            "category": "Informática",
            "brand": "ABC",
            "product_url": "https://example.com/products/abc-ultra"
        },
        {
            "title": "Fone de Ouvido QWE Noise",
            "description": "Fone de ouvido com cancelamento de ruído, Bluetooth 5.0 e bateria de longa duração",
            "price": 599.90,
            "category": "Áudio",
            "brand": "QWE",
            "product_url": "https://example.com/products/qwe-noise"
        }
    ]
    
    # Pontuar produtos
    scored_products = score_products(sample_products, MyLLM.GTP4o_mini)
    
    # Imprimir resultado
    print(json.dumps(scored_products, indent=2, ensure_ascii=False))
