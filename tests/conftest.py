# tests/conftest.py
import pytest

@pytest.fixture
def stores():
    return [
        {
            "name": "Amazon Test",
            "platform": "amazon",
            "api_credentials": {"affiliate_url": "https://amazon.com.br/test"}
        }
    ]

@pytest.fixture
def products():
    return [
        {
            "external_id": "test123",
            "platform": "amazon",
            "title": "Test Product",
            "description": "A test product",
            "price": 99.90,
            "product_url": "https://amazon.com.br/product/test123",
            "category": "Eletrônicos",
            "available": True,
            "rank": 1,
            "score": 9.2
        }
    ]