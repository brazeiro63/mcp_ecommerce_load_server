# app/api/endpoints/discover_stores.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.db.session import get_db
from app.models.affiliate_store import AffiliateStore
from app.schemas.affiliate_store import AffiliateStoreCreate, AffiliateStoreInDB
from app.repositories.affiliate_store_repository import AffiliateStoreRepository
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, WebsiteSearchTool
from dotenv import load_dotenv
from store_selection_crew import ResearchStores
from utils.MyLLM import MyLLM
import json

# Carregar variáveis de ambiente
load_dotenv()

router = APIRouter()

# Inicializar ferramentas necessárias
scraper_tool = SerperDevTool()
scraper_tool.n_results = 20
web_rag_tool = WebsiteSearchTool()

# Definir modelo de linguagem
llm = MyLLM.GTP4o_mini

@router.post("/discover", response_model=Dict[str, Any])
def discover_stores(
    country: str,
    niche: str,
    period: str = "junho de 2024 a maio 2025",
    db: Session = Depends(get_db)
):
    """
    Endpoint para descobrir lojas de afiliados com base no país, nicho e período.
    Utiliza CrewAI para realizar a pesquisa e salva os resultados no banco de dados.
    """
    try:
        # Instanciar a classe de pesquisa
        researche_stores = ResearchStores()
        
        # Preparar os inputs para a pesquisa
        inputs = {"country": country, "period": period, "niche": niche}
        
        # Executar a pesquisa
        result = researche_stores.store_selection_crew().kickoff(inputs=inputs)
        
        # Criar instância do repositório
        repo = AffiliateStoreRepository(db)
        
        # Salvar resultados no banco de dados
        created_stores = repo.bulk_create_from_crew_results(result)
        
        # Converter modelos para schemas para a resposta
        store_responses = [
            {
                "id": store.id,
                "name": store.name,
                "platform": store.platform,
                "active": store.active,
                "created_at": store.created_at
            }
            for store in created_stores
        ]
        
        return {
            "status": "success", 
            "raw_result": result,
            "stores_created": len(created_stores),
            "stores": store_responses
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante a descoberta de lojas: {str(e)}")


@router.post("/discover-async", response_model=Dict[str, str])
async def discover_stores_async(
    background_tasks: BackgroundTasks,
    country: str,
    niche: str,
    period: str = "junho de 2024 a maio 2025",
    db: Session = Depends(get_db)
):
    """
    Versão assíncrona do endpoint de descoberta de lojas.
    Executa a pesquisa em background e retorna imediatamente.
    """
    def run_discovery(country: str, niche: str, period: str, db: Session):
        try:
            # Instanciar a classe de pesquisa
            researche_stores = ResearchStores()
            
            # Preparar os inputs para a pesquisa
            inputs = {"country": country, "period": period, "niche": niche}
            
            # Executar a pesquisa
            result = researche_stores.store_selection_crew().kickoff(inputs=inputs)
            
            # Criar instância do repositório
            repo = AffiliateStoreRepository(db)
            
            # Salvar resultados no banco de dados
            created_stores = repo.bulk_create_from_crew_results(result)
            
            print(f"Pesquisa concluída. {len(created_stores)} lojas criadas.")
        except Exception as e:
            print(f"Erro durante a descoberta de lojas: {str(e)}")
    
    # Adicionar a tarefa ao background
    background_tasks.add_task(run_discovery, country, niche, period, db)
    
    return {
        "status": "processing",
        "message": f"Descoberta de lojas para {niche} em {country} iniciada em background."
    }

@router.get("/list", response_model=List[AffiliateStoreInDB])
def list_affiliate_stores(
    db: Session = Depends(get_db),
    skip: int = 0, 
    limit: int = 100
):
    """
    Lista as lojas afiliadas salvas no banco de dados.
    """
    stores = db.query(AffiliateStore).offset(skip).limit(limit).all()
    return stores