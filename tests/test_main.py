from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Testa se o endpoint raiz ('/') está funcionando corretamente."""
    response = client.get("/")
    assert response.status_code == 200 # Estamos apenas verificando se o get foi bem sucedido
    #assert response.json() == {"message": "Alguma mensagem que queiramos colocar"}