from fastapi import APIRouter

from src.app.api.endpoints import discover_affiliate_stores

api_router = APIRouter()
api_router.include_router(discover_affiliate_stores.router, prefix="/discover_affiliate_stores", tags="discover_affiliate_stores")