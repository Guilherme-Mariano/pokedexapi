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

# --- Fixtures do Pytest para um Ambiente de Teste Limpo e Isolado ---

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture que cria todas as tabelas antes de cada teste e as destrói depois.
    Isso garante total isolamento entre os testes.
    """
    Base.metadata.create_all(bind=engine) # Cria as tabelas
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine) # Destrói as tabelas

@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture que cria um TestClient e sobrescreve a dependência get_db
    para usar o banco de dados de teste limpo fornecido pela fixture db_session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear() # Limpa a sobrescrita


# --- Início dos Testes das Rotas (agora recebem a fixture 'client') ---

# Dados de exemplo que podemos reutilizar
santo_data_exemplo = {
    "nome": "São Francisco de Assis", "protecao": "Animais e Natureza",
    "festa_liturgica": "2025-10-04", "veneracao": "Igreja Católica",
    "local_de_nascimento": "Assis, Itália", "data_de_nascimento": "1182-01-01",
    "data_de_morte": "1226-10-03", "historia": "Fundador da ordem dos Franciscanos.",
    "atribuicoes": "Pássaros, Lobo"
}

def test_create_santo_endpoint(client):
    """Testa a criação de um santo com sucesso."""
    response = client.post("/santos/", json=santo_data_exemplo)
    
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["nome"] == santo_data_exemplo["nome"]
    assert "id" in data

def test_get_santo_by_id_endpoint(client):
    """Testa a busca de um santo por ID."""
    # 1. Cria um santo primeiro para garantir que ele exista
    response_create = client.post("/santos/", json=santo_data_exemplo)
    assert response_create.status_code == 201
    santo_id = response_create.json()["id"]

    # 2. Agora, busca por esse ID
    response_get = client.get(f"/santos/{santo_id}")
    assert response_get.status_code == 200
    data = response_get.json()
    assert data["id"] == santo_id
    assert data["nome"] == santo_data_exemplo["nome"]

def test_get_santo_by_name_endpoint(client):
    """Testa a busca de um santo pelo nome (case-insensitive)."""
    # 1. Cria o santo
    client.post("/santos/", json=santo_data_exemplo)
    
    # 2. Busca pelo nome com letras minúsculas
    response = client.get("/santos/são francisco de assis")
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["nome"] == "São Francisco de Assis"

def test_get_all_santos_endpoint(client):
    """Testa a listagem de todos os santos."""
    # 1. Cria dois santos para popular a lista
    client.post("/santos/", json=santo_data_exemplo)
    
    client.post("/santos/", json={
        "nome": "São Jorge",
        "protecao": "Soldados, Escoteiros",
        "festa_liturgica": "2025-04-23",
        "veneracao": "Igreja Católica, Igreja Ortodoxa, Comunhão Anglicana",
        "local_de_nascimento": "Capadócia, Turquia",
        "data_de_nascimento": "0275-01-01",
        "data_de_morte": "0303-04-23",
        "historia": "Lendário soldado romano e mártir cristão, famoso por ter matado o dragão.",
        "atribuicoes": "Dragão, Lança, Cavalo Branco"
    })
    
    # 2. Busca a lista completa
    response = client.get("/santos/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    # O serviço ordena por nome, então Francisco vem antes de Jorge.
    assert data[0]["nome"] == "São Francisco de Assis"
    assert data[1]["nome"] == "São Jorge"

def test_get_santo_not_found(client):
    """Testa se a API retorna 404 para um santo que não existe."""
    response = client.get("/santos/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Santo não encontrado"

def test_update_santo_endpoint(client):
    """Testa a atualização parcial de um santo com sucesso."""
    # 1. Cria o santo que será atualizado
    response_create = client.post("/santos/", json=santo_data_exemplo)
    santo_id = response_create.json()["id"]

    # 2. Define os dados da atualização parcial
    update_data = {"protecao": "Protetor da Ecologia", "historia": "Nova história atualizada."}

    # 3. Faz a requisição PATCH
    response_update = client.patch(f"/santos/{santo_id}", json=update_data)
    
    # 4. Verifica a resposta
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["id"] == santo_id
    assert data["protecao"] == "Protetor da Ecologia"
    assert data["historia"] == "Nova história atualizada."
    assert data["nome"] == santo_data_exemplo["nome"]

def test_update_santo_not_found(client):
    """Testa se a atualização de um santo inexistente retorna 404."""
    response = client.patch("/santos/9999", json={"nome": "Fantasma"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Santo não encontrado"

def test_delete_santo_endpoint(client):
    """Testa a deleção de um santo com sucesso."""
    # 1. Cria o santo que será deletado
    response_create = client.post("/santos/", json=santo_data_exemplo)
    santo_id = response_create.json()["id"]
    
    # 2. Deleta o santo
    response_delete = client.delete(f"/santos/{santo_id}")
    
    # 3. Verifica a resposta da deleção
    assert response_delete.status_code == 204
    
    # 4. Verificação extra: tenta buscar o santo deletado, deve retornar 404
    response_get = client.get(f"/santos/{santo_id}")
    assert response_get.status_code == 404

def test_delete_santo_not_found(client):
    """Testa se a deleção de um santo inexistente retorna 404."""
    response = client.delete("/santos/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Santo não encontrado"