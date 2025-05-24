# /main.py
import os

from dotenv import load_dotenv

from crews.product_discovery_crew import ProductDiscoveryCrew
from crews.store_selection_crew import ResearchStores

# Carregar variáveis de ambiente
load_dotenv()

def main():
    # Parâmetros do fluxo
    country = 'Brasil'
    period = 'junho de 2024 a maio 2025'
    niche = 'produtos infantís'
    inputs = {"country": country, "period": period, "niche": niche}

    # Etapa 1: Seleção de lojas
    store_selector = ResearchStores()
    store_result = store_selector.store_selection_crew().kickoff(inputs=inputs)
    print(f'Lojas Selecionadas:\n{store_result}\n')

    # Etapa 2: Inserção, identificação de produtos e scraping
    product_crew = ProductDiscoveryCrew()
    final_result = product_crew.run_full_discovery(inputs)
    print(f'Resultado Final:\n{final_result}')

if __name__ == "__main__":
    main()
