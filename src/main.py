# /main.py
import os

from dotenv import load_dotenv

from src.crews.product_discovery_crew import ProductDiscoveryCrew
from src.crews.store_selection_crew import ResearchStores

# Carregar variáveis de ambiente
load_dotenv()

def main():
    # Parâmetros do fluxo
    country = 'Brasil'
    period = 'junho de 2024 a maio 2025'
    niche = 'produtos infantís'
    inputs = {"country": country, "period": period, "niche": niche}

    # Etapa 1: Seleção de lojas
    store_selection_crew = ResearchStores().store_selection_crew()
    store_result = store_selection_crew().kickoff(inputs=inputs)
    print(f'Lojas Selecionadas:\n{store_result}\n')

    # Atualizar inputs com as URLs das lojas selecionadas
    inputs["stores"] = [store.split(",")[1].strip() for store in store_result]

    stores_input = ", ".join(inputs["stores"])
    print(f'Lojas selecionadas (string): {stores_input}')

    # # Etapa 2: Inserção, identificação de produtos e scraping
    # product_selection_crew = ProductDiscovery().product_selection_crew()
    # final_result = product_selection_crew().kickoff(inputs=stores_input)
    # print(f'Resultado Final:\n{final_result}')

if __name__ == "__main__":
    main()
