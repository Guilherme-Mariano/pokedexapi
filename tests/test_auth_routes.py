# tests/test_auth_routes.py

import pytest

@pytest.fixture(scope="function")
def authenticated_user_token(client):
    """
    Fixture reutilizável que cria um usuário, faz login e retorna seu ID e token.
    Versão robusta que pega o ID real da resposta da criação.
    """
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    # Cria o usuário e captura a resposta para obter o ID real
    response_create = client.post("/users/", json=user_data)
    assert response_create.status_code == 201
    created_user_id = response_create.json()["id"]
    
    # Faz login para obter o token
    login_response = client.post("/token", data={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Retorna o ID real do usuário criado e seu token
    return {"token": token, "user_id": created_user_id, "username": "testuser"}

# --- Testes para as Rotas de Usuário e Autenticação ---

def test_create_user_route(client):
    """Testa a criação de um usuário pela rota /users/."""
    response = client.post("/users/", json={
        "username": "routeuser",
        "email": "route@test.com",
        "password": "pwd"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "routeuser"
    assert data["email"] == "route@test.com"
    assert "id" in data
    assert "password" not in data # Garante que a senha não é retornada

def test_login_for_access_token(client):
    """Testa o login e a geração de token."""
    user_data = {"username": "loginuser", "email": "login@test.com", "password": "pwd"}
    client.post("/users/", json=user_data)
    
    response = client.post("/token", data={"username": "loginuser", "password": "pwd"})
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

# --- NOVOS TESTES ADICIONADOS ---

def test_update_own_user_success(client, authenticated_user_token):
    """Testa se um usuário consegue atualizar seus próprios dados com sucesso."""
    token = authenticated_user_token["token"]
    user_id = authenticated_user_token["user_id"]
    
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"email": "new.email@example.com"}
    
    response = client.patch(f"/users/{user_id}", json=update_data, headers=headers)
    
    assert response.status_code == 200
    # Verifica se o e-mail foi realmente atualizado na resposta
    assert response.json()["email"] == "new.email@example.com"
    # Garante que o username não mudou
    assert response.json()["username"] == authenticated_user_token["username"]

def test_delete_own_user_success(client, authenticated_user_token):
    """Testa se um usuário consegue deletar a própria conta com sucesso."""
    token = authenticated_user_token["token"]
    user_id = authenticated_user_token["user_id"]
    user_credentials = {
        "username": authenticated_user_token["username"],
        "password": "password123" # A senha original do usuário
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Deleta o usuário
    response_delete = client.delete(f"/users/{user_id}", headers=headers)
    assert response_delete.status_code == 204 # No Content
    
    # 2. VERIFICAÇÃO CRUCIAL: Tenta fazer login novamente com o usuário deletado. Deve falhar.
    login_response = client.post("/token", data=user_credentials)
    assert login_response.status_code == 401 # Unauthorized


def test_update_other_user_forbidden(client, authenticated_user_token):
    """Testa se um usuário recebe erro 403 ao tentar atualizar outro usuário."""
    token_user1 = authenticated_user_token["token"]
    
    # Cria um segundo usuário
    response_create = client.post("/users/", json={"username": "user2", "email": "user2@test.com", "password": "pwd"})
    user2_id = response_create.json()["id"]
    
    # Usuário 1 (logado) tenta atualizar o Usuário 2
    headers = {"Authorization": f"Bearer {token_user1}"}
    update_data = {"email": "hacked@example.com"}
    
    response = client.patch(f"/users/{user2_id}", json=update_data, headers=headers)
    assert response.status_code == 403