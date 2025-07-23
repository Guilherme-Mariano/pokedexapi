# tests/test_auth_routes.py

# A fixture 'client' é fornecida automaticamente pelo tests/conftest.py

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
    assert "password" not in data

def test_login_for_access_token(client):
    """Testa o login e a geração de token."""
    user_data = {"username": "loginuser", "email": "login@test.com", "password": "pwd"}
    client.post("/users/", json=user_data)
    
    response = client.post("/token", data={"username": "loginuser", "password": "pwd"})
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

def test_update_own_user_success(client):
    """Testa se um usuário consegue atualizar seus próprios dados com sucesso."""
    # 1. Setup: Cria um usuário único para este teste e faz login
    user_data = {"username": "update_user", "email": "update@test.com", "password": "pwd123"}
    response_create = client.post("/users/", json=user_data)
    user_id = response_create.json()["id"]
    
    login_response = client.post("/token", data={"username": user_data["username"], "password": user_data["password"]})
    token = login_response.json()["access_token"]
    
    # 2. Ação: Tenta atualizar o e-mail do próprio usuário
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"email": "new.email.for.update@example.com"}
    
    response = client.patch(f"/users/{user_id}", json=update_data, headers=headers)
    
    # 3. Verificação
    assert response.status_code == 200
    assert response.json()["email"] == "new.email.for.update@example.com"
    assert response.json()["username"] == "update_user"

def test_delete_own_user_success(client):
    """Testa se um usuário consegue deletar a própria conta com sucesso."""
    # 1. Setup: Cria um usuário único e faz login
    user_data = {"username": "delete_user", "email": "delete@test.com", "password": "pwd123"}
    response_create = client.post("/users/", json=user_data)
    user_id = response_create.json()["id"]
    
    login_response = client.post("/token", data={"username": user_data["username"], "password": user_data["password"]})
    token = login_response.json()["access_token"]

    # 2. Ação: Deleta o usuário
    headers = {"Authorization": f"Bearer {token}"}
    response_delete = client.delete(f"/users/{user_id}", headers=headers)
    
    # 3. Verificação
    assert response_delete.status_code == 204
    
    # Verificação crucial: Tenta fazer login novamente, deve falhar
    failed_login_response = client.post("/token", data={"username": user_data["username"], "password": user_data["password"]})
    assert failed_login_response.status_code == 401

def test_update_other_user_forbidden(client):
    """Testa se um usuário recebe erro 403 ao tentar atualizar outro usuário."""
    # 1. Setup: Cria dois usuários distintos
    user_a_data = {"username": "userA_updater", "email": "usera@test.com", "password": "pwdA"}
    client.post("/users/", json=user_a_data)

    user_b_data = {"username": "userB_target", "email": "userb@test.com", "password": "pwdB"}
    response_create_b = client.post("/users/", json=user_b_data)
    user_b_id = response_create_b.json()["id"]
    
    # 2. Faz login como Usuário A para obter seu token
    login_response_a = client.post("/token", data={"username": user_a_data["username"], "password": user_a_data["password"]})
    token_a = login_response_a.json()["access_token"]
    
    # 3. Ação: Usuário A tenta atualizar o Usuário B
    headers = {"Authorization": f"Bearer {token_a}"}
    update_data = {"email": "hacked@example.com"}
    
    response = client.patch(f"/users/{user_b_id}", json=update_data, headers=headers)
    
    # 4. Verificação
    assert response.status_code == 403
    #assert response.status_code == 200