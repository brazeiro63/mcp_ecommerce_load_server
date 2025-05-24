# app/main.py
# No início do seu arquivo app/main.py
import logging
from logging.handlers import RotatingFileHandler

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.api.endpoints import discover_affiliate_stores
from src.app.db.session import Base, engine
from src.crews.product_discovery_crew import ProductDiscoveryCrew
from src.crews.store_selection_crew import ResearchStores

# Configurar logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file = 'app_logs.txt'

# Criar handler para arquivo
file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

# Obter o logger raiz e adicionar o handler
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.setLevel(logging.DEBUG)

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

router = APIRouter()

@router.get("/run-complete-discovery")
def run_discovery(country: str, period: str, niche: str):
    inputs = {"country": country, "period": period, "niche": niche}
    
    # Etapa 1
    store_selector = ResearchStores()
    store_result = store_selector.store_selection_crew().kickoff(inputs=inputs)

    # Etapa 2
    product_crew = ProductDiscoveryCrew()
    final_result = product_crew.run_full_discovery(inputs)

    return {
        "stores": store_result,
        "products": final_result
    }