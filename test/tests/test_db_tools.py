import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app.db.insert_affiliate_stores import insert_affiliate_stores
from src.app.db.insert_products import insert_products


def test_insert_affiliate_store():
    sample_store = [{
        "name": "Test Store",
        "platform": "TestPlatform",
        "active": True,
        "api_credentials": {"token": "123abc"}
    }]
    result = insert_affiliate_stores(sample_store)
    assert len(result) == 1
    assert result[0].name == "Test Store"

def test_insert_product():
    sample_product = [{
        "external_id": "abc123",
        "platform": "TestPlatform",
        "title": "Test Product",
        "description": "A test product",
        "price": 19.99,
        "product_url": "http://example.com/product",
        "category": "Testing"
    }]
    result = insert_products(sample_product, affiliate_store_name="Test Store")
    assert len(result) == 1
    assert result[0].title == "Test Product"