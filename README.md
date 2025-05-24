# MCP E-commerce Load Server

## Visão Geral

O MCP E-commerce Load Server é uma solução integrada para descoberta, validação e cadastro de lojas de afiliados e seus produtos em um sistema de e-commerce. O sistema utiliza inteligência artificial através do framework CrewAI para automatizar processos de pesquisa, validação e priorização de dados.

## Fluxo de Funcionamento

O sistema segue o seguinte fluxo de trabalho:

1. Descoberta de lojas usando Serper API
2. Validação inteligente das lojas usando CrewAI
3. Cadastro das lojas no banco de dados (PostgreSQL/SQLAlchemy)
4. Coleta de produtos via Serper MCP Server
5. Priorização inteligente dos produtos usando CrewAI
6. Curadoria humana opcional (via interface CSV/dashboard)
7. Carga final no banco de dados

## Requisitos

- Python 3.12 ou superior
- PostgreSQL
- Chaves de API para serviços externos (OpenAI, Serper, etc.)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/brazeiro63/mcp_ecommerce_load_server.git
cd mcp_ecommerce_load_server
```

2. Instale as dependências:
```bash
pip install -e .
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API e configurações
```

4. Execute o servidor:
```bash
python main.py
```

## Estrutura do Projeto

```graphql
project_root/
│
├── main.py                 # Orquestra a pipeline de povoamento
├── requirements.txt        # Dependências do projeto
├── pyproject.toml          # Configuração do projeto
├── crew_agents/            # Agentes de IA para descoberta e pontuação
├── app/                    # Aplicação principal
│   ├── api/                # Endpoints da API
│   ├── db/                 # Configurações de banco de dados
│   ├── models/             # Modelos de dados
│   ├── repositories/       # Camada de acesso a dados
│   ├── schemas/            # Esquemas de validação
│   └── main.py             # Ponto de entrada da aplicação
├── config/                 # Arquivos de configuração
├── review_interface/       # Interface para revisão humana
└── utils/                  # Utilitários
```

## Uso

O sistema pode ser executado de duas formas:

1. **Modo completo**: Executa todo o pipeline de descoberta, validação e carga
```bash
python main.py
```

2. **Modo seletivo**: Executa apenas partes específicas do pipeline
```bash
python main.py --only-discover  # Apenas descoberta de lojas
python main.py --only-products  # Apenas coleta de produtos
```

## Contribuição

Contribuições são bem-vindas! Por favor, siga estas etapas:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add some amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

---

## ✅ 2. Criando os Testes

### 🧪 Caminho sugerido: `tests/test_db_tools.py`

Crie esse arquivo com:

```python
# tests/test_db_tools.py
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
