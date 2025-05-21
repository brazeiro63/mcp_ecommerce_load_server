# app/repositories/affiliate_store_repository.py
import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.affiliate_store import AffiliateStore


class AffiliateStoreRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, store_data: Dict[str, Any]) -> AffiliateStore:
        """
        Cria um novo registro de loja afiliada no banco de dados.
        """
        # Garantir que temos o formato apropriado para api_credentials
        api_credentials = store_data.get("api_credentials", {})
        if not api_credentials:
            api_credentials = {"default": "none"}
            
        # Criar a instância do modelo
        db_store = AffiliateStore(
            name=store_data["name"],
            platform=store_data["platform"],
            api_credentials=api_credentials,
            active=store_data.get("active", True)
        )
        
        # Adicionar à sessão e persistir
        self.db.add(db_store)
        self.db.commit()
        self.db.refresh(db_store)
        
        return db_store
    
    def get_by_name_and_platform(self, name: str, platform: str) -> Optional[AffiliateStore]:
        """
        Busca uma loja afiliada pelo nome e plataforma.
        """
        return self.db.query(AffiliateStore).filter(
            AffiliateStore.name == name,
            AffiliateStore.platform == platform
        ).first()
    
    def bulk_create_from_crew_results(self, results: str) -> List[AffiliateStore]:
        """
        Processa os resultados da pesquisa CrewAI e cria múltiplas lojas afiliadas.
        """
        created_stores = []
        
        # Parsear o texto do resultado para extrair informações relevantes
        # O formato exato dependerá da saída do CrewAI, mas vamos assumir um formato simples
        store_entries = self._parse_crew_results(results)
        
        for store_data in store_entries:
            # Verificar se a loja já existe
            existing_store = self.get_by_name_and_platform(
                store_data["name"], 
                store_data["platform"]
            )
            
            if not existing_store:
                # Criar nova loja se não existir
                created_store = self.create(store_data)
                created_stores.append(created_store)
                
        return created_stores
    
    def _parse_crew_results(self, results: str) -> List[Dict[str, Any]]:
        """
        Parse os resultados do CrewAI para extrair informações das lojas.
        Esta função precisa ser adaptada com base no formato específico da saída.
        """
        store_entries = []
        
        # Assumindo que os resultados estão em um formato de lista numerada ou com marcadores
        # Vamos tentar extrair nome, plataforma e URL
        
        lines = results.strip().split("\n")
        current_store = {}
        
        for line in lines:
            line = line.strip()
            
            # Identificar possível início de um novo item na lista
            if line.startswith("- ") or line.startswith("* ") or (line[0].isdigit() and line[1] == "."):
                if current_store and "name" in current_store:
                    store_entries.append(current_store)
                current_store = {}
                
                # Tentar extrair o nome da loja (assumindo que está no início da linha após o marcador)
                name_part = line[2:].strip() if line.startswith("- ") or line.startswith("* ") else line[line.find(".")+1:].strip()
                current_store["name"] = name_part.split(" - ")[0] if " - " in name_part else name_part
                
            # Procurar por links de plataforma ou afiliação
            elif "http" in line.lower():
                url = line[line.find("http"):].split(" ")[0].strip()
                if url.endswith("."):
                    url = url[:-1]
                    
                # Tentar determinar a plataforma a partir da URL
                platform = "unknown"
                if "amazon" in url.lower():
                    platform = "amazon"
                elif "mercadolivre" in url.lower() or "mercadolibre" in url.lower():
                    platform = "mercadolivre"
                elif "aliexpress" in url.lower():
                    platform = "aliexpress"
                elif "shopee" in url.lower():
                    platform = "shopee"
                elif "magalu" in url.lower() or "magazineluiza" in url.lower():
                    platform = "magalu"
                
                current_store["platform"] = current_store.get("platform", platform)
                current_store["api_credentials"] = {"affiliate_url": url}
        
        # Adicionar o último item se existir
        if current_store and "name" in current_store:
            store_entries.append(current_store)
        
        # Garantir que todos os itens tenham os campos obrigatórios
        return [
            store for store in store_entries 
            if "name" in store and "platform" in store and "api_credentials" in store
        ]