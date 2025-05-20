"""
Módulo para inserção de produtos no banco de dados.
Fornece funções para persistir dados de produtos coletados e pontuados.
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from app.models.product import Product
from app.models.affiliate_store import AffiliateStore
from app.db.session import get_db

def insert_product(product_data: Dict[str, Any], db: Session, affiliate_store_id: Optional[int] = None) -> Product:
    """
    Insere um único produto no banco de dados.
    
    Args:
        product_data: Dicionário com dados do produto
        db: Sessão do banco de dados
        affiliate_store_id: ID da loja afiliada (opcional)
        
    Returns:
        Product: Objeto do produto inserido
    """
    # Extrair dados básicos
    title = product_data.get('title', '')
    external_id = product_data.get('external_id', '')
    platform = product_data.get('platform', 'generic')
    
    # Verificar se o produto já existe
    existing_product = None
    if external_id:
        existing_product = db.query(Product).filter(
            Product.external_id == external_id,
            Product.platform == platform
        ).first()
    
    if not existing_product and title:
        existing_product = db.query(Product).filter(
            Product.title == title,
            Product.platform == platform
        ).first()
    
    if existing_product:
        # Atualizar produto existente
        existing_product.title = title
        existing_product.description = product_data.get('description', '')
        existing_product.price = product_data.get('price', 0.0)
        existing_product.sale_price = product_data.get('sale_price')
        existing_product.image_url = product_data.get('image_url', '')
        existing_product.product_url = product_data.get('product_url', '')
        existing_product.affiliate_url = product_data.get('affiliate_url', '')
        existing_product.category = product_data.get('category', '')
        existing_product.brand = product_data.get('brand', '')
        existing_product.available = product_data.get('available', True)
        
        # Atualizar loja afiliada se fornecida
        if affiliate_store_id:
            existing_product.affiliate_store_id = affiliate_store_id
        
        existing_product.updated_at = datetime.now()
        db.commit()
        db.refresh(existing_product)
        return existing_product
    
    # Criar novo produto
    new_product = Product(
        external_id=external_id,
        platform=platform,
        title=title,
        description=product_data.get('description', ''),
        price=product_data.get('price', 0.0),
        sale_price=product_data.get('sale_price'),
        image_url=product_data.get('image_url', ''),
        product_url=product_data.get('product_url', ''),
        affiliate_url=product_data.get('affiliate_url', ''),
        category=product_data.get('category', ''),
        brand=product_data.get('brand', ''),
        available=product_data.get('available', True),
        affiliate_store_id=affiliate_store_id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

def insert_products(products_data: List[Dict[str, Any]], 
                   affiliate_store_name: Optional[str] = None,
                   db_session: Optional[Session] = None) -> List[Product]:
    """
    Insere múltiplos produtos no banco de dados.
    
    Args:
        products_data: Lista de dicionários com dados dos produtos
        affiliate_store_name: Nome da loja afiliada (opcional)
        db_session: Sessão do banco de dados (opcional)
        
    Returns:
        List[Product]: Lista de objetos dos produtos inseridos
    """
    # Usar sessão fornecida ou criar uma nova
    if db_session:
        return _insert_products_with_session(products_data, affiliate_store_name, db_session)
    else:
        # Usar context manager para garantir fechamento da sessão
        db = next(get_db())
        try:
            return _insert_products_with_session(products_data, affiliate_store_name, db)
        finally:
            db.close()

def _insert_products_with_session(products_data: List[Dict[str, Any]], 
                                 affiliate_store_name: Optional[str],
                                 db: Session) -> List[Product]:
    """
    Função auxiliar para inserir produtos usando uma sessão específica.
    
    Args:
        products_data: Lista de dicionários com dados dos produtos
        affiliate_store_name: Nome da loja afiliada (opcional)
        db: Sessão do banco de dados
        
    Returns:
        List[Product]: Lista de objetos dos produtos inseridos
    """
    inserted_products = []
    
    # Buscar ID da loja afiliada se o nome for fornecido
    affiliate_store_id = None
    if affiliate_store_name:
        store = db.query(AffiliateStore).filter(AffiliateStore.name == affiliate_store_name).first()
        if store:
            affiliate_store_id = store.id
    
    for product_data in products_data:
        # Processar dados do produto para garantir formato correto
        processed_data = _process_product_data(product_data)
        
        # Inserir produto
        product = insert_product(processed_data, db, affiliate_store_id)
        inserted_products.append(product)
    
    return inserted_products

def _process_product_data(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa e valida os dados do produto antes da inserção.
    
    Args:
        product_data: Dicionário com dados do produto
        
    Returns:
        Dict[str, Any]: Dicionário processado e validado
    """
    processed_data = product_data.copy()
    
    # Garantir que o título existe
    if 'title' not in processed_data or not processed_data['title']:
        if 'name' in processed_data and processed_data['name']:
            processed_data['title'] = processed_data['name']
        else:
            processed_data['title'] = "Produto sem título"
    
    # Garantir que o preço é numérico
    if 'price' in processed_data:
        try:
            if isinstance(processed_data['price'], str):
                # Remover símbolos de moeda e converter para float
                price_str = processed_data['price'].replace('R$', '').replace('$', '').replace('.', '').replace(',', '.')
                processed_data['price'] = float(price_str)
        except:
            processed_data['price'] = 0.0
    
    # Garantir que o preço de venda é numérico
    if 'sale_price' in processed_data and processed_data['sale_price']:
        try:
            if isinstance(processed_data['sale_price'], str):
                # Remover símbolos de moeda e converter para float
                price_str = processed_data['sale_price'].replace('R$', '').replace('$', '').replace('.', '').replace(',', '.')
                processed_data['sale_price'] = float(price_str)
        except:
            processed_data['sale_price'] = None
    
    # Extrair plataforma da URL se disponível e não especificada
    if 'platform' not in processed_data and 'product_url' in processed_data:
        url = processed_data['product_url'].lower()
        if 'amazon' in url:
            processed_data['platform'] = 'amazon'
        elif 'mercadolivre' in url or 'mercadolibre' in url:
            processed_data['platform'] = 'mercadolivre'
        elif 'magalu' in url or 'magazineluiza' in url:
            processed_data['platform'] = 'magalu'
        elif 'americanas' in url:
            processed_data['platform'] = 'americanas'
        elif 'shopee' in url:
            processed_data['platform'] = 'shopee'
        else:
            processed_data['platform'] = 'other'
    
    return processed_data


# Exemplo de uso
if __name__ == "__main__":
    # Dados de exemplo
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
        }
    ]
    
    # Inserir produtos
    inserted = insert_products(sample_products, "Amazon Brasil")
    
    # Imprimir resultado
    for product in inserted:
        print(f"Produto inserido: {product.title} (ID: {product.id})")
