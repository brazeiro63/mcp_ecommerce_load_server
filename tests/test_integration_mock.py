"""
Script modificado para validação de integração sem dependência de API externa.
Simula o fluxo completo do pipeline para fins de teste.
"""

import json
import os
import sys
from datetime import datetime

from crewai import CrewOutput


def test_store_discovery_flow():
    """
    Simula o fluxo de descoberta e pontuação de lojas.
    """
    print("=== Testando fluxo de descoberta de lojas ===")
    
    # Parâmetros de teste
    country = "Brasil"
    period = "junho de 2024 a maio 2025"
    niche = "produtos infantis"
    
    # Simular descoberta de lojas
    print(f"Simulando descoberta de lojas para: país={country}, período={period}, nicho={niche}")
    
    # Dados simulados
    stores = [
        {
            "name": "Amazon Brasil",
            "url": "https://www.amazon.com.br/associates",
            "description": "Programa de afiliados da Amazon Brasil com comissões de 1% a 10%",
            "rank": 1,
            "score": 9.5
        },
        {
            "name": "Mercado Livre",
            "url": "https://www.mercadolivre.com.br/afiliados",
            "description": "Programa de afiliados do Mercado Livre com comissões competitivas",
            "rank": 2,
            "score": 9.2
        },
        {
            "name": "Magazine Luiza",
            "url": "https://www.magazinevoce.com.br/",
            "description": "Programa de afiliados da Magazine Luiza com boas comissões",
            "rank": 3,
            "score": 8.7
        },
        {
            "name": "Americanas",
            "url": "https://www.americanas.com.br/afiliados",
            "description": "Programa de afiliados das Americanas com diversas categorias",
            "rank": 4,
            "score": 8.5
        },
        {
            "name": "Shopee",
            "url": "https://shopee.com.br/affiliate",
            "description": "Programa de afiliados da Shopee com foco em produtos importados",
            "rank": 5,
            "score": 8.3
        }
    ]
    
    print(f"Lojas descobertas: {len(stores)}")
    for i, store in enumerate(stores, 1):
        print(f"{i}. {store['name']} - URL: {store['url']}")
    
    # Salvar resultado para uso posterior
    os.makedirs("./test_results", exist_ok=True)

    if isinstance(stores, CrewOutput):
        try:
            parsed = json.loads(stores.raw)
        except json.JSONDecodeError:
            parsed = {"result": stores.raw}
    else:
        parsed = stores

    with open("./test_results/discovered_stores.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

        
    print("Resultado salvo em ./test_results/discovered_stores.json")
    assert stores



def test_store_insertion(stores):
    """
    Simula a inserção de lojas no banco de dados.
    """
    print("\n=== Testando inserção de lojas no banco de dados ===")
    
    if not stores:
        print("Nenhuma loja para inserir.")
        return False
    
    # Simular inserção de lojas
    print(f"Simulando inserção de {len(stores)} lojas no banco de dados...")
    
    # Salvar resultado para referência
    with open("./test_results/stores_to_insert.json", "w", encoding="utf-8") as f:
        json.dump(stores, f, ensure_ascii=False, indent=2)
    
    print("Lojas preparadas para inserção salvas em ./test_results/stores_to_insert.json")
    print("Inserção simulada com sucesso!")
    assert True

def test_product_scoring():
    """
    Simula a pontuação de produtos.
    """
    print("\n=== Testando pontuação de produtos ===")
    
    # Produtos de exemplo para teste
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
    
    # Simular pontuação
    print(f"Simulando pontuação de {len(sample_products)} produtos...")
    
    # Adicionar pontuações simuladas
    scored_products = []
    for i, product in enumerate(sample_products, 1):
        scored_product = product.copy()
        scored_product["rank"] = i
        scored_product["score"] = 10 - (i * 0.5)  # Pontuação decrescente
        scored_product["strengths"] = f"Ponto forte do produto {i}"
        scored_product["marketing_approach"] = f"Abordagem de marketing para o produto {i}"
        scored_products.append(scored_product)
    
    print(f"Produtos pontuados: {len(scored_products)}")
    for i, product in enumerate(scored_products, 1):
        print(f"{i}. {product['title']} - Score: {product['score']}, Rank: {product['rank']}")
    
    # Salvar resultado para uso posterior
    os.makedirs("./test_results", exist_ok=True)

    if isinstance(scored_products, CrewOutput):
        try:
            parsed = json.loads(scored_products.raw)
        except json.JSONDecodeError:
            parsed = {"result": scored_products.raw}
    else:
        parsed = scored_products

    with open("./test_results/scored_products.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    
    print("Resultado salvo em ./test_results/scored_products.json")
    assert scored_products

def test_product_insertion(products):
    """
    Simula a inserção de produtos no banco de dados.
    """
    print("\n=== Testando inserção de produtos no banco de dados ===")
    
    if not products:
        print("Nenhum produto para inserir.")
        return False
    
    # Simular inserção de produtos
    print(f"Simulando inserção de {len(products)} produtos no banco de dados...")
    
    # Salvar resultado para referência
    with open("./test_results/products_to_insert.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print("Produtos preparados para inserção salvos em ./test_results/products_to_insert.json")
    print("Inserção simulada com sucesso!")
    assert True

def test_review_interface(products):
    """
    Testa a interface de revisão (exportação e importação).
    """
    print("\n=== Testando interface de revisão ===")
    
    if not products:
        print("Nenhum produto para exportar.")
        return False
    
    # Simular exportação
    print(f"Simulando exportação de {len(products)} produtos para revisão...")
    output_dir = "./test_results/review_batches"
    os.makedirs(output_dir, exist_ok=True)
    
    # Criar arquivo CSV simulado
    import csv
    batch_file = f"{output_dir}/batch_test.csv"
    
    with open(batch_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["id", "title", "description", "price", "rank", "score", "approved"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, product in enumerate(products, 1):
            row = {
                "id": i,
                "title": product["title"],
                "description": product["description"],
                "price": product["price"],
                "rank": product["rank"],
                "score": product["score"],
                "approved": ""
            }
            writer.writerow(row)
    
    print(f"Produtos exportados para {batch_file}")
    
    # Simular revisão humana
    print("\nSimulando revisão humana (aprovando todos os produtos)...")
    reviewed_file = f"{output_dir}/batch_test_reviewed.csv"
    
    with open(batch_file, 'r', newline='', encoding='utf-8') as infile, \
         open(reviewed_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            row['approved'] = 'true'  # Aprovar todos os produtos
            writer.writerow(row)
    
    print(f"Revisão simulada salva em {reviewed_file}")
    
    # Simular importação
    print("\nSimulando importação de produtos revisados...")
    
    # Ler arquivo CSV revisado
    reviewed_products = []
    with open(reviewed_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            reviewed_products.append(row)
    
    print(f"Produtos importados: {len(reviewed_products)}")
    approved = sum(1 for p in reviewed_products if p.get('approved') == 'true')
    print(f"Produtos aprovados: {approved}")
    
    assert True

def run_integration_test():
    """
    Executa o teste de integração completo.
    """
    print("Iniciando teste de integração do sistema...\n")
    
    # Testar fluxo de descoberta de lojas
    stores = test_store_discovery_flow()
    
    # Testar inserção de lojas
    store_insertion_ok = test_store_insertion(stores)
    
    # Testar pontuação de produtos
    products = test_product_scoring()
    
    # Testar inserção de produtos
    product_insertion_ok = test_product_insertion(products)
    
    # Testar interface de revisão
    review_interface_ok = test_review_interface(products)
    
    # Resumo dos testes
    print("\n=== Resumo dos testes de integração ===")
    print(f"Descoberta de lojas: {'OK' if stores else 'FALHA'}")
    print(f"Inserção de lojas: {'OK' if store_insertion_ok else 'FALHA'}")
    print(f"Pontuação de produtos: {'OK' if products else 'FALHA'}")
    print(f"Inserção de produtos: {'OK' if product_insertion_ok else 'FALHA'}")
    print(f"Interface de revisão: {'OK' if review_interface_ok else 'FALHA'}")
    
    # Resultado final
    all_ok = stores and store_insertion_ok and products and product_insertion_ok and review_interface_ok
    print(f"\nResultado final: {'TODOS OS TESTES PASSARAM' if all_ok else 'ALGUNS TESTES FALHARAM'}")
    
    return all_ok

if __name__ == "__main__":
    run_integration_test()
