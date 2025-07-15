# tests/test_santos_routes.py

# As fixtures 'client' e 'db_session' são importadas automaticamente do conftest.py

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
    response_create = client.post("/santos/", json=santo_data_exemplo)
    santo_id = response_create.json()["id"]

    response_get = client.get(f"/santos/{santo_id}")
    assert response_get.status_code == 200
    data = response_get.json()
    assert data["id"] == santo_id
    assert data["nome"] == santo_data_exemplo["nome"]

def test_get_santo_by_name_endpoint(client):
    """Testa a busca de um santo pelo nome (case-insensitive)."""
    client.post("/santos/", json=santo_data_exemplo)
    response = client.get("/santos/são francisco de assis")
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["nome"] == "São Francisco de Assis"

def test_get_all_santos_endpoint(client):
    """Testa a listagem de todos os santos."""
    client.post("/santos/", json=santo_data_exemplo)
    client.post("/santos/", json={
        "nome": "São Jorge", "protecao": "Soldados, Escoteiros",
        "festa_liturgica": "2025-04-23", "veneracao": "Igreja Católica",
        "local_de_nascimento": "Capadócia, Turquia", "data_de_nascimento": "0275-01-01",
        "data_de_morte": "0303-04-23", "historia": "Lendário soldado romano.", "atribuicoes": "Dragão, Lança"
    })
    
    response = client.get("/santos/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["nome"] == "São Francisco de Assis"
    assert data[1]["nome"] == "São Jorge"

def test_get_santo_not_found(client):
    """Testa se a API retorna 404 para um santo que não existe."""
    response = client.get("/santos/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Santo não encontrado"

def test_update_santo_endpoint(client):
    """Testa a atualização parcial de um santo com sucesso."""
    response_create = client.post("/santos/", json=santo_data_exemplo)
    santo_id = response_create.json()["id"]

    update_data = {"protecao": "Protetor da Ecologia", "historia": "Nova história atualizada."}
    response_update = client.patch(f"/santos/{santo_id}", json=update_data)
    
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["protecao"] == "Protetor da Ecologia"
    assert data["nome"] == santo_data_exemplo["nome"]

def test_update_santo_not_found(client):
    """Testa se a atualização de um santo inexistente retorna 404."""
    response = client.patch("/santos/9999", json={"nome": "Fantasma"})
    assert response.status_code == 404

def test_delete_santo_endpoint(client):
    """Testa a deleção de um santo com sucesso."""
    response_create = client.post("/santos/", json=santo_data_exemplo)
    santo_id = response_create.json()["id"]
    
    response_delete = client.delete(f"/santos/{santo_id}")
    assert response_delete.status_code == 204
    
    response_get = client.get(f"/santos/{santo_id}")
    assert response_get.status_code == 404

def test_delete_santo_not_found(client):
    """Testa se a deleção de um santo inexistente retorna 404."""
    response = client.delete("/santos/9999")
    assert response.status_code == 404