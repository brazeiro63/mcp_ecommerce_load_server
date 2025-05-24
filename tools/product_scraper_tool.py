from crewai.tools import tool
from typing import List
import requests
from bs4 import BeautifulSoup

@tool("ScrapeStoreProductsTool")
def scrape_store_products(store_url: str, product_names: List[str]) -> str:
    """
    Acessa a loja pela URL e coleta até 100 produtos relacionados aos nomes fornecidos.
    Retorna os produtos em formato JSON prontos para uso com ProductCreate.
    """
    scraped_products = []
    
    for name in product_names:
        # Exemplo genérico de scraping
        response = requests.get(f"{store_url}/search?q={name}")
        if response.status_code != 200:
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".product")  # ajustar conforme a loja real

        for item in items[:20]:  # limitar por produto por busca
            try:
                scraped_products.append({
                    "external_id": item.get("data-id", ""),
                    "platform": store_url,
                    "title": item.select_one(".product-title").get_text(strip=True),
                    "description": item.select_one(".product-description").get_text(strip=True),
                    "price": float(item.select_one(".product-price").get_text(strip=True).replace("R$", "").replace(",", ".")),
                    "sale_price": None,
                    "image_url": item.select_one("img")["src"],
                    "product_url": store_url + item.select_one("a")["href"],
                    "category": name,
                    "brand": None,
                    "available": True
                })
            except Exception as e:
                continue

            if len(scraped_products) >= 100:
                break

    return str(scraped_products[:100])
