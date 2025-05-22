"""
Módulo para importação de revisões humanas de produtos.
Fornece funções para importar produtos revisados de formatos como CSV ou JSON.
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

def import_review_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Importa um arquivo de revisão de produtos.
    
    Args:
        file_path: Caminho do arquivo a ser importado
        
    Returns:
        List[Dict[str, Any]]: Lista de produtos revisados
    """
    # Determinar formato com base na extensão
    if file_path.lower().endswith('.json'):
        return _import_from_json(file_path)
    elif file_path.lower().endswith('.csv'):
        return _import_from_csv(file_path)
    else:
        raise ValueError(f"Formato de arquivo não suportado: {file_path}")

def _import_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Importa produtos de um arquivo CSV.
    
    Args:
        file_path: Caminho do arquivo CSV
        
    Returns:
        List[Dict[str, Any]]: Lista de produtos revisados
    """
    products = []
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Converter campos numéricos
            for field in ['price', 'sale_price', 'score']:
                if field in row and row[field]:
                    try:
                        row[field] = float(row[field])
                    except ValueError:
                        pass
            
            # Converter campo de aprovação para booleano
            if 'approved' in row:
                approved_value = row['approved'].lower().strip()
                if approved_value in ['true', 'yes', 'sim', '1', 'verdadeiro']:
                    row['approved'] = True
                elif approved_value in ['false', 'no', 'não', '0', 'falso']:
                    row['approved'] = False
                else:
                    row['approved'] = None
            
            products.append(row)
    
    return products

def _import_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Importa produtos de um arquivo JSON.
    
    Args:
        file_path: Caminho do arquivo JSON
        
    Returns:
        List[Dict[str, Any]]: Lista de produtos revisados
    """
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        products = json.load(jsonfile)
    
    return products

def import_reviewed_products(file_paths: List[str] = None, 
                            review_dir: str = "./review_batches",
                            only_approved: bool = False) -> List[Dict[str, Any]]:
    """
    Função principal para importar produtos revisados.
    
    Args:
        file_paths: Lista de caminhos de arquivos a serem importados (opcional)
        review_dir: Diretório de revisão (usado se file_paths não for fornecido)
        only_approved: Se True, retorna apenas produtos aprovados
        
    Returns:
        List[Dict[str, Any]]: Lista de produtos revisados
    """
    all_products = []
    
    # Se não foram fornecidos caminhos específicos, buscar arquivos no diretório
    if not file_paths:
        if not os.path.exists(review_dir):
            return []
        
        # Buscar arquivos CSV e JSON no diretório
        file_paths = []
        for file in os.listdir(review_dir):
            if file.lower().endswith(('.csv', '.json')):
                file_paths.append(os.path.join(review_dir, file))
    
    # Importar cada arquivo
    for file_path in file_paths:
        try:
            products = import_review_file(file_path)
            all_products.extend(products)
        except Exception as e:
            print(f"Erro ao importar arquivo {file_path}: {e}")
    
    # Filtrar apenas produtos aprovados se solicitado
    if only_approved:
        all_products = [p for p in all_products if p.get('approved') is True]
    
    return all_products

def get_latest_review_batch(review_dir: str = "./review_batches") -> Optional[str]:
    """
    Obtém o lote de revisão mais recente.
    
    Args:
        review_dir: Diretório de revisão
        
    Returns:
        Optional[str]: Caminho do arquivo mais recente ou None se não houver
    """
    if not os.path.exists(review_dir):
        return None
    
    # Buscar arquivos CSV e JSON no diretório
    files = []
    for file in os.listdir(review_dir):
        if file.lower().endswith(('.csv', '.json')):
            file_path = os.path.join(review_dir, file)
            files.append((file_path, os.path.getmtime(file_path)))
    
    # Ordenar por data de modificação (mais recente primeiro)
    files.sort(key=lambda x: x[1], reverse=True)
    
    # Retornar o mais recente ou None se não houver
    return files[0][0] if files else None


# Exemplo de uso
if __name__ == "__main__":
    # Importar produtos revisados
    latest_batch = get_latest_review_batch()
    
    if latest_batch:
        print(f"Importando lote mais recente: {latest_batch}")
        products = import_reviewed_products([latest_batch])
        
        # Contar produtos aprovados e rejeitados
        approved = sum(1 for p in products if p.get('approved') is True)
        rejected = sum(1 for p in products if p.get('approved') is False)
        pending = sum(1 for p in products if p.get('approved') is None)
        
        print(f"Total de produtos: {len(products)}")
        print(f"Aprovados: {approved}")
        print(f"Rejeitados: {rejected}")
        print(f"Pendentes: {pending}")
    else:
        print("Nenhum lote de revisão encontrado.")
