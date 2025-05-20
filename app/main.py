# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import discover_affiliate_stores
from app.db.session import Base, engine

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicializar o aplicativo FastAPI
app = FastAPI(
    title="E-commerce Affiliate Platform API",
    description="API para descoberta e gerenciamento de lojas afiliadas e produtos",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir para origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir os routers
app.include_router(discover_affiliate_stores.router, prefix="/api/stores", tags=["stores"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de E-commerce de Afiliados"}