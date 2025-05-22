# app/api/endpoints/discover_stores.py
import json
import re
from typing import Any, Dict, List, Union

from crewai import Agent, Crew, CrewOutput, Process, Task
from crewai_tools import SerperDevTool, WebsiteSearchTool
from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.affiliate_store import AffiliateStore
from app.repositories.affiliate_store_repository import \
    AffiliateStoreRepository
from app.schemas.affiliate_store import (AffiliateStoreCreate,
                                         AffiliateStoreInDB)
from store_selection_crew import ResearchStores
from utils.MyLLM import MyLLM

# Carregar variáveis de ambiente
load_dotenv()

router = APIRouter()

# Inicializar ferramentas necessárias
scraper_tool = SerperDevTool()
scraper_tool.n_results = 20
web_rag_tool = WebsiteSearchTool()

# Definir modelo de linguagem
llm = MyLLM.GTP4o_mini

def _to_plain_text(result: Union[str, "CrewOutput"]) -> str:
    """
    Garante que o resultado vindo da Crew seja texto.
    - Se já for str → devolve.
    - Se for CrewOutput → tenta .content ou converte via str().
    """
    if isinstance(result, str):
        return result
    # CrewOutput costuma ter .content ou .result; ajuste conforme sua lib
    for attr in ("content", "text", "result"):
        if hasattr(result, attr):
            return getattr(result, attr)
    return str(result)  # fallback

def _normalize_crew_output(crew_out) -> list[dict]:
    raw = getattr(crew_out, "output", str(crew_out)).strip()

    # 1) tenta JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 2) fallback – bullet list “- **Nome** … (URL)”
    stores = []
    for blk in re.split(r"\n-\s+\*\*", raw):
        if not blk: continue
        name = re.match(r"([^*]+)\*\*", blk)
        url  = re.search(r"\((https?://[^\)]+)\)", blk)
        if name and url:
            stores.append({"name": name.group(1).strip(),
                           "affiliate_url": url.group(1)})
    return stores


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
        inputs = {"country": country, "period": period, "niche": niche}
        
        raw_output = ResearchStores().store_selection_crew().kickoff(inputs=inputs)
        stores_data = _normalize_crew_output(raw_output)
        plain_text = _to_plain_text(stores_data)

        repo = AffiliateStoreRepository(db)
        created_stores = repo.bulk_create_from_crew_results(plain_text)

        print(f"[Discover_affiliate_atores.py] CREATED STORES: {plain_text}")

        return {
            "status": "success",
            "raw_result": plain_text,
            "stores_created": len(created_stores),
            "stores": [
                {
                    "id": s.id,
                    "name": s.name,
                    "platform": s.platform,
                    "active": s.active,
                    "created_at": s.created_at,
                }
                for s in created_stores
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro durante a descoberta de lojas: {e}"
        )


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
            inputs = {"country": country, "period": period, "niche": niche}
            raw_output = ResearchStores().store_selection_crew().kickoff(inputs=inputs)
            plain_text = _to_plain_text(raw_output)

            repo = AffiliateStoreRepository(db)
            created_stores = repo.bulk_create_from_crew_results(plain_text)
            print(f"[Discover_affiliate_atores.py] CREATED STORES: {plain_text}")


            print(f"Pesquisa concluída. {len(created_stores)} lojas criadas.")
        except Exception as e:
            print(f"Erro durante a descoberta de lojas: {e}")

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