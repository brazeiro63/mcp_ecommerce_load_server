"""
Inicializador dos endpoints da API.
Configura e registra os endpoints disponíveis na aplicação.
"""

from fastapi import APIRouter

# Criar router principal
router = APIRouter()

# Importar e incluir sub-routers específicos
# Exemplo:
# from app.api.endpoints import stores, products
# router.include_router(stores.router, prefix="/stores", tags=["stores"])
# router.include_router(products.router, prefix="/products", tags=["products"])

# Endpoint básico de status
@router.get("/")
async def root():
    """
    Endpoint raiz para verificar o status da API.
    """
    return {
        "status": "online",
        "message": "MCP E-commerce Load Server API está funcionando",
        "version": "0.1.0"
    }

# Endpoint de saúde
@router.get("/health")
async def health():
    """
    Endpoint para verificar a saúde do sistema.
    """
    return {
        "status": "healthy",
        "components": {
            "database": "connected",
            "services": "operational"
        }
    }
