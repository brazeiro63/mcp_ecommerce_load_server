from typing import Dict, List

from crewai.tools import tool

from app.db.insert_affiliate_stores import insert_affiliate_stores
from app.db.insert_products import insert_products


@tool("InsertAffiliateStoresTool")
def insert_affiliate_stores_tool(stores: List[Dict]) -> str:
    """
    Insert a list of affiliate stores into the database.
    Expects each item to match the AffiliateStoreCreate schema.
    """
    try:
        inserted = insert_affiliate_stores(stores)
        return f"{len(inserted)} affiliate stores successfully inserted."
    except Exception as e:
        return f"Failed to insert affiliate stores: {e}"


@tool("InsertProductsTool")
def insert_products_tool(products_by_store: Dict[str, List[Dict]]) -> str:
    """
    Insert products grouped by store into the database.
    The key must be the store name, and the value must be a list of products following ProductCreate schema.
    """
    total_inserted = 0
    try:
        for store_name, products in products_by_store.items():
            inserted = insert_products(products_data=products, affiliate_store_name=store_name)
            total_inserted += len(inserted)
        return f"{total_inserted} products inserted across {len(products_by_store)} stores."
    except Exception as e:
        return f"Failed to insert products: {e}"
