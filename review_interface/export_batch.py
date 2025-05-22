"""
Módulo para exportação de lotes de produtos para revisão humana.
Fornece funções para exportar produtos para formatos como CSV ou JSON.
"""

import csv
import json
import os

<<<<<<< HEAD
from datetime import datetime
from typing import Any, Dict, List, Optional

=======
from datetime import datetime
from typing import Any, Dict, List, Optional

>>>>>>> d4728ad (Melhorias e acesso ao banco de dados)

def export_batch(products: List[Dict[str, Any]], 
                format: str = "csv", 
                output_dir: str = "./review_batches",
                batch_name: Optional[str] = None) -> str:
    """
    Exporta um lote de produtos para revisão humana.
    
    Args:
        products: Lista de produtos a serem exportados
        format: Formato de exportação ('csv' ou 'json')
        output_dir: Diretório de saída
        batch_name: Nome do lote (opcional)
        
    Returns:
        str: Caminho do arquivo exportado
    """
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Gerar nome do lote se não fornecido
    if not batch_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_name = f"batch_{timestamp}"
    
    # Determinar caminho do arquivo
    if format.lower() == "json":
        file_path = os.path.join(output_dir, f"{batch_name}.json")
        _export_to_json(products, file_path)
    else:  # csv é o padrão
        file_path = os.path.join(output_dir, f"{batch_name}.csv")
        _export_to_csv(products, file_path)
    
    return file_path

def _export_to_csv(products: List[Dict[str, Any]], file_path: str) -> None:
    """
    Exporta produtos para formato CSV.
    
    Args:
        products: Lista de produtos
        file_path: Caminho do arquivo de saída
    """
    # Definir campos a serem exportados
    fields = [
        "id", "title", "description", "price", "sale_price", 
        "category", "brand", "product_url", "affiliate_url", 
        "image_url", "platform", "rank", "score", "approved"
    ]
    
    # Adicionar campo de aprovação para revisão
    for product in products:
        if "approved" not in product:
            product["approved"] = ""  # Campo a ser preenchido na revisão
    
    # Escrever arquivo CSV
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for product in products:
            writer.writerow(product)

def _export_to_json(products: List[Dict[str, Any]], file_path: str) -> None:
    """
    Exporta produtos para formato JSON.
    
    Args:
        products: Lista de produtos
        file_path: Caminho do arquivo de saída
    """
    # Adicionar campo de aprovação para revisão
    for product in products:
        if "approved" not in product:
            product["approved"] = None  # Campo a ser preenchido na revisão
    
    # Escrever arquivo JSON
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(products, jsonfile, ensure_ascii=False, indent=2)

def export_for_review(products: List[Dict[str, Any]], 
                     format: str = "csv", 
                     output_dir: str = "./review_batches",
                     batch_name: Optional[str] = None,
                     max_batch_size: int = 100) -> List[str]:
    """
    Função principal para exportar produtos para revisão humana.
    Divide em múltiplos lotes se necessário.
    
    Args:
        products: Lista de produtos a serem exportados
        format: Formato de exportação ('csv' ou 'json')
        output_dir: Diretório de saída
        batch_name: Prefixo do nome do lote (opcional)
        max_batch_size: Tamanho máximo de cada lote
        
    Returns:
        List[str]: Lista de caminhos dos arquivos exportados
    """
    # Gerar prefixo do lote se não fornecido
    if not batch_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_name = f"batch_{timestamp}"
    
    # Dividir em lotes se necessário
    batch_files = []
    
    if len(products) <= max_batch_size:
        # Exportar como um único lote
        file_path = export_batch(products, format, output_dir, batch_name)
        batch_files.append(file_path)
    else:
        # Dividir em múltiplos lotes
        for i in range(0, len(products), max_batch_size):
            batch_products = products[i:i+max_batch_size]
            batch_file_name = f"{batch_name}_part{i//max_batch_size + 1}"
            file_path = export_batch(batch_products, format, output_dir, batch_file_name)
            batch_files.append(file_path)
    
    return batch_files


# Exemplo de uso
if __name__ == "__main__":
    # Produtos de exemplo
    sample_products = [
        {
            "id": 1,
            "title": "Smartphone XYZ Pro",
            "description": "Smartphone de última geração com câmera de 108MP",
            "price": 2999.90,
            "category": "Eletrônicos",
            "brand": "XYZ",
            "product_url": "https://example.com/products/xyz-pro",
            "rank": 1,
            "score": 9.5
        },
        {
            "id": 2,
            "title": "Notebook ABC Ultra",
            "description": "Notebook ultrafino com processador Intel i7",
            "price": 5499.90,
            "category": "Informática",
            "brand": "ABC",
            "product_url": "https://example.com/products/abc-ultra",
            "rank": 2,
            "score": 8.7
        }
    ]
    
    # Exportar para revisão
    batch_files = export_for_review(sample_products, format="csv")
    
    # Imprimir resultado
    for file_path in batch_files:
        print(f"Lote exportado: {file_path}")
