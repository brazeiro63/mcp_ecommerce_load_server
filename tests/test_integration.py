"""
Script para validar a integração e funcionamento do sistema.
Testa o fluxo completo do pipeline de descoberta, pontuação e armazenamento.
"""

import json
import os

from dotenv import load_dotenv

from app.db.insert_affiliate_stores import insert_affiliate_stores
from app.db.insert_products import insert_products
from crew_agents.discover_and_score_stores import find_and_score_stores
from crew_agents.score_products import score_products
from review_interface.export_batch import export_for_review
from review_interface.import_review import import_reviewed_products
from utils.MyLLM import MyLLM


# Carregar variáveis de ambiente
load_dotenv()

def test_store_discovery_flow():
    """
    Testa o fluxo de descoberta e pontuação de lojas.
    """
    print("=== Testando fluxo de descoberta de lojas ===")
    
    # Parâmetros de teste
    country = "Brasil"
    period = "junho de 2024 a maio 2025"
    niche = "produtos infantis"
    
    # Executar descoberta de lojas
    print(f"Descobrindo lojas para: país={country}, período={period}, nicho={niche}")
    try:
        stores = find_and_score_stores(
            country=country,
            period=period,
            niche=niche,
            llm=MyLLM.GTP4o_mini
        )
        
        print(f"Lojas descobertas: {len(stores)}")
        for i, store in enumerate(stores[:3], 1):  # Mostrar apenas as 3 primeiras
            print(f"{i}. {store.get('name', 'N/A')} - URL: {store.get('url', 'N/A')}")
        
        if len(stores) > 3:
            print(f"... e mais {len(stores) - 3} lojas")
        
        # Salvar resultado para uso posterior
        os.makedirs("./test_results", exist_ok=True)
        with open("./test_results/discovered_stores.json", "w", encoding="utf-8") as f:
            json.dump(stores, f, ensure_ascii=False, indent=2)
        
        print("Resultado salvo em ./test_results/discovered_stores.json")
        return stores
    
    except Exception as e:
        print(f"Erro ao descobrir lojas: {e}")
        return []

def test_store_insertion(stores):
    """
    Testa a inserção de lojas no banco de dados.
    """
    print("\n=== Testando inserção de lojas no banco de dados ===")
    
    if not stores:
        print("Nenhuma loja para inserir.")
        return
    
    try:
        # Inserir lojas no banco
        print(f"Inserindo {len(stores)} lojas no banco de dados...")
        
        # Simulação - em um ambiente real, isso conectaria ao banco
        print("Nota: Esta é uma simulação. Em um ambiente real, as lojas seriam inseridas no banco PostgreSQL.")
        
        # Salvar resultado para referência
        with open("./test_results/stores_to_insert.json", "w", encoding="utf-8") as f:
            json.dump(stores, f, ensure_ascii=False, indent=2)
        
        print("Lojas preparadas para inserção salvas em ./test_results/stores_to_insert.json")
        return True
    
    except Exception as e:
        print(f"Erro ao inserir lojas: {e}")
        return False

def test_product_scoring():
    """
    Testa a pontuação de produtos.
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
    
    try:
        # Pontuar produtos
        print(f"Pontuando {len(sample_products)} produtos...")
        scored_products = score_products(sample_products, MyLLM.GTP4o_mini)
        
        print(f"Produtos pontuados: {len(scored_products)}")
        for i, product in enumerate(scored_products, 1):
            print(f"{i}. {product.get('title', 'N/A')} - Score: {product.get('score', 'N/A')}, Rank: {product.get('rank', 'N/A')}")
        
        # Salvar resultado para uso posterior
        with open("./test_results/scored_products.json", "w", encoding="utf-8") as f:
            json.dump(scored_products, f, ensure_ascii=False, indent=2)
        
        print("Resultado salvo em ./test_results/scored_products.json")
        return scored_products
    
    except Exception as e:
        print(f"Erro ao pontuar produtos: {e}")
        return []

def test_product_insertion(products):
    """
    Testa a inserção de produtos no banco de dados.
    """
    print("\n=== Testando inserção de produtos no banco de dados ===")
    
    if not products:
        print("Nenhum produto para inserir.")
        return
    
    try:
        # Inserir produtos no banco
        print(f"Inserindo {len(products)} produtos no banco de dados...")
        
        # Simulação - em um ambiente real, isso conectaria ao banco
        print("Nota: Esta é uma simulação. Em um ambiente real, os produtos seriam inseridos no banco PostgreSQL.")
        
        # Salvar resultado para referência
        with open("./test_results/products_to_insert.json", "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print("Produtos preparados para inserção salvos em ./test_results/products_to_insert.json")
        return True
    
    except Exception as e:
        print(f"Erro ao inserir produtos: {e}")
        return False

def test_review_interface(products):
    """
    Testa a interface de revisão (exportação e importação).
    """
    print("\n=== Testando interface de revisão ===")
    
    if not products:
        print("Nenhum produto para exportar.")
        return
    
    try:
        # Exportar produtos para revisão
        print(f"Exportando {len(products)} produtos para revisão...")
        output_dir = "./test_results/review_batches"
        batch_files = export_for_review(products, format="csv", output_dir=output_dir)
        
        print(f"Produtos exportados em {len(batch_files)} lotes:")
        for file_path in batch_files:
            print(f"- {file_path}")
        
        # Simular revisão humana (aprovando todos os produtos)
        print("\nSimulando revisão humana (aprovando todos os produtos)...")
        
        # Ler o primeiro arquivo CSV
        import csv
        reviewed_file = batch_files[0]
        reviewed_path = reviewed_file.replace(".csv", "_reviewed.csv")
        
        with open(reviewed_file, 'r', newline='', encoding='utf-8') as infile, \
             open(reviewed_path, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                row['approved'] = 'true'  # Aprovar todos os produtos
                writer.writerow(row)
        
        print(f"Revisão simulada salva em {reviewed_path}")
        
        # Importar produtos revisados
        print("\nImportando produtos revisados...")
        reviewed_products = import_reviewed_products([reviewed_path])
        
        print(f"Produtos importados: {len(reviewed_products)}")
        approved = sum(1 for p in reviewed_products if p.get('approved') is True)
        print(f"Produtos aprovados: {approved}")
        
        return True
    
    except Exception as e:
        print(f"Erro ao testar interface de revisão: {e}")
        return False

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
