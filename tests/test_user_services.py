# tests/test_santos_routes.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.models import saint_model, user_model 

# --- Configuração do Banco de Dados de Teste em Memória ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Fixture para criar as tabelas antes de cada teste e limpá-las depois.
    Isso garante que cada teste comece com um banco de dados limpo.
    """
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """
    Fixture que cria um TestClient para a aplicação, sobrescrevendo
    a dependência get_db para usar o banco de dados de teste.
    """
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # Limpa a sobrescrita depois que o teste termina
    app.dependency_overrides.clear()


# --- Início dos Testes das Rotas (agora recebem a fixture 'client') ---

def test_create_santo_endpoint(client):
    """Testa a rota POST /santos/ para criar um novo santo."""
    # (Este teste agora é público, sem necessidade de token)
    santo_data = {
        "nome": "São João Batista", "protecao": "Amizade", "festa_liturgica": "2025-06-24",
        "veneracao": "Igreja Católica, Igreja Ortodoxa", "local_de_nascimento": "Ein Karem",
        "data_de_nascimento": "0008-01-01", "data_de_morte": "0030-01-01",
        "historia": "Pregador judeu.", "atribuicoes": "Cordeiro, Concha"
    }
    response = client.post("/santos/", json=santo_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["nome"] == santo_data["nome"]
    assert "id" in data

def test_get_santo_by_id_endpoint(client):
    """Testa a rota GET /santos/{id} para buscar um santo pelo ID."""
    santo_data = {"nome": "São Pedro", "protecao": "Pescadores", "festa_liturgica": "2025-06-24",
        "veneracao": "Igreja Católica, Igreja Ortodoxa", "local_de_nascimento": "Ein Karem",
        "data_de_nascimento": "0008-01-01", "data_de_morte": "0030-01-01",
        "historia": "Pregador judeu.", "atribuicoes": "Cordeiro, Concha"} 
    response = client.post("/santos/", json=santo_data)
    santo_id = response.json()["id"]

    # Agora, busca pelo ID
    response = client.get(f"/santos/{santo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == santo_id
    assert data["nome"] == "São Pedro"

def test_get_santo_not_found(client):
    """Testa se a API retorna 404 para um santo que não existe."""
    response = client.get("/santos/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Santo não encontrado"