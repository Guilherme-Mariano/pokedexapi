# tests/test_santos_routes.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app  # Importa a instância principal da aplicação
from app.db.database import Base, get_db
from app.schemas.saint_schema import SantosCreate
import datetime

# --- Configuração do Banco de Dados de Teste em Memória ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria as tabelas no banco de dados em memória antes de qualquer teste
Base.metadata.create_all(bind=engine)

# --- Fixture e Sobrescrita da Dependência ---

def override_get_db():
    """
    Uma função de dependência que usa o banco de dados de teste em memória.
    Ela garante que cada teste tenha uma sessão de banco de dados limpa.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Diz à nossa aplicação FastAPI para usar o banco de dados de teste
# em vez do banco de dados de produção/desenvolvimento durante os testes.
app.dependency_overrides[get_db] = override_get_db

# Cria um cliente de teste que pode fazer "chamadas de rede" para nossa API
client = TestClient(app)

# --- Início dos Testes das Rotas ---

def test_create_santo_endpoint():
    """
    Testa a rota POST /santos/ para criar um novo santo.
    """
    # 1. Prepara os dados do novo santo a ser criado
    santo_data = {
        "nome": "São João Batista",
        "protecao": "Amizade",
        "festa_liturgica": "2025-06-24",
        "veneracao": "Igreja Católica, Igreja Ortodoxa",
        "local_de_nascimento": "Ein Karem",
        "data_de_nascimento": "0008-01-01", # Datas aproximadas
        "data_de_morte": "0030-01-01",
        "historia": "Pregador judeu e um asceta. É descrito como o precursor de Jesus.",
        "atribuicoes": "Cordeiro, Concha"
    }
    
    # 2. Faz a requisição POST para o endpoint
    response = client.post("/santos/", json=santo_data)
    
    # 3. Verifica a resposta
    assert response.status_code == 201, response.text
    
    data = response.json()
    assert data["nome"] == santo_data["nome"]
    assert data["protecao"] == santo_data["protecao"]
    assert "id" in data
    assert isinstance(data["id"], int)

def test_get_santo_by_id_endpoint():
    """
    Testa a rota GET /santos/{id} para buscar um santo pelo ID.
    """
    # Usaremos o santo criado no teste anterior, que terá o ID 1,
    # pois o banco de dados é recriado para cada sessão de teste.
    response = client.get("/santos/1")
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1
    assert data["nome"] == "São João Batista"

def test_get_santo_by_name_endpoint():
    """
    Testa a rota GET /santos/{name} para buscar um santo pelo nome.
    """
    response = client.get("/santos/são joão batista") # Testando case-insensitivity
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["nome"] == "São João Batista"
    assert data["id"] == 1

def test_get_santo_not_found():
    """
    Testa se a API retorna 404 para um santo que não existe.
    """
    response = client.get("/santos/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Santo não encontrado"}

def test_get_all_santos_endpoint():
    """
    Testa a rota GET /santos/ para listar todos os santos.
    """
    # Primeiro, vamos criar um segundo santo para garantir que a lista funcione
    client.post("/santos/", json={
        "nome": "Santa Teresinha",
        "protecao": "Missões, Floristas",
        "festa_liturgica": "2025-10-01",
        "veneracao": "Igreja Católica",
        "local_de_nascimento": "Alençon, França",
        "data_de_nascimento": "1873-01-02",
        "data_de_morte": "1897-09-30",
        "historia": "Conhecida como Santa Teresa do Menino Jesus e da Santa Face.",
        "atribuicoes": "Rosas"
    })
    
    response = client.get("/santos/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2 # Devemos ter dois santos cadastrados agora