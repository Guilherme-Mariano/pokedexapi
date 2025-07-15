# tests/test_auth_routes.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.models import user_model, saint_model

# --- Configuração do Banco de Dados de Teste (Pode ser movida para conftest.py no futuro) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixtures do Pytest ---

@pytest.fixture(scope="function")
def db_session():
    """Garante um banco de dados limpo para cada teste."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Fornece um TestClient com a dependência de banco de dados sobrescrita."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def authenticated_user_token(client):
    """
    Fixture reutilizável que cria um usuário, faz login e retorna seu ID e token.
    """
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    # Cria o usuário
    client.post("/users/", json=user_data)
    
    # Faz login para obter o token
    login_response = client.post("/token", data={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    
    token = login_response.json()["access_token"]
    
    # Para testar, precisamos saber o ID do usuário criado.
    # Como é o primeiro, o ID será 1.
    return {"token": token, "user_id": 1, "username": "testuser"}


# --- Testes para a Rota de Update (PATCH /users/{user_id}) ---

def test_update_own_user_success(client, authenticated_user_token):
    """Testa se um usuário consegue atualizar seus próprios dados com sucesso."""
    token = authenticated_user_token["token"]
    user_id = authenticated_user_token["user_id"]
    
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"email": "new.email@example.com"}
    
    response = client.patch(f"/users/{user_id}", json=update_data, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["email"] == "new.email@example.com"
    # O username não foi alterado, então deve continuar o mesmo
    assert response.json()["username"] == "testuser"

def test_update_other_user_forbidden(client, authenticated_user_token):
    """Testa se um usuário recebe erro 403 ao tentar atualizar outro usuário."""
    # Usuário 1 (logado)
    token_user1 = authenticated_user_token["token"]
    
    # Cria um segundo usuário
    client.post("/users/", json={"username": "user2", "email": "user2@test.com", "password": "pwd"})
    user2_id = 2 # Será o segundo usuário criado no BD de teste
    
    # Usuário 1 tenta atualizar o e-mail do Usuário 2
    headers = {"Authorization": f"Bearer {token_user1}"}
    update_data = {"email": "hacked@example.com"}
    
    response = client.patch(f"/users/{user2_id}", json=update_data, headers=headers)
    
    assert response.status_code == 403 # Forbidden!
    assert response.json()["detail"] == "Não tem permissão para modificar este usuário."


# --- Testes para a Rota de Delete (DELETE /users/{user_id}) ---

def test_delete_own_user_success(client, authenticated_user_token):
    """Testa se um usuário consegue deletar a própria conta."""
    token = authenticated_user_token["token"]
    user_id = authenticated_user_token["user_id"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Deleta o usuário
    response = client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 204 # No Content

    # Verificação: Tenta fazer login novamente com o usuário deletado. Deve falhar.
    login_response = client.post("/token", data={
        "username": "testuser",
        "password": "password123"
    })
    assert login_response.status_code == 401 # Unauthorized!

def test_delete_other_user_forbidden(client, authenticated_user_token):
    """Testa se um usuário recebe erro 403 ao tentar deletar outro usuário."""
    # Usuário 1 (logado)
    token_user1 = authenticated_user_token["token"]
    
    # Cria um segundo usuário
    client.post("/users/", json={"username": "user2_to_delete", "email": "user2del@test.com", "password": "pwd"})
    user2_id = 2
    
    # Usuário 1 tenta deletar o Usuário 2
    headers = {"Authorization": f"Bearer {token_user1}"}
    response = client.delete(f"/users/{user2_id}", headers=headers)
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Não tem permissão para deletar este usuário."