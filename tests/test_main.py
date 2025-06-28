from fastapi.testclient import TestClient
from app.main import app # Instância do que vamos testar

# O objeto client fará requisições a API
client = TestClient(app)

def test_read_root():
    """Testa se o endpoint raiz ('/') está funcionando corretamente."""
    response = client.get("/")
    assert response.status_code == 200 # Estamos apenas verificando se o get foi bem sucedido
    assert response.json() == {"message": "Bem-vindo à Pokédex API!"} # Verificando se a API devolveu a mensagem de boas vindas ( Talvez desnecessário )

def test_get_all_pokemon():
    """ 
        Testando o endpoint que retorna o banco inteiro
    """
    response = client.get("/pokemon")
    assert response.status_code == 200 # Mesma verificação
    assert isinstance(response.json(), list) # Checando se de fato a API entregou uma lista
    assert response.json() # Checando se não está vazia 

# Fazendo um test em um pokemon específico. Verificando a integridade do model
def test_get_pikachu_by_name():
    """Testa a busca de um pokemon pelo nome."""
    response = client.get("/pokemon/pikachu")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Pikachu"
    assert data["id"] == 25

def test_get_charmander_by_id():
    """Testa a busca de um pokemon pelo ID."""
    response = client.get("/pokemon/4")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Charmander"
    assert data["id"] == 4

# Checando se a api retorna resposta adequada a um request de pokemon que não está no banco
def test_pokemon_not_found():
    """Testa se a API retorna 404 para um pokemon não listado."""
    response = client.get("/pokemon/pokeinexistente")
    assert response.status_code == 404
    assert response.json() == {"detail": "Pokémon Não Encontrado"}

# ----------------------------------- IMPELEMNTAR TEST DOS MODELS DEPOIS ... -----------------------------------
