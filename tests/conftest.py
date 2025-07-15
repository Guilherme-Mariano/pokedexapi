# tests/conftest.py

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


# --- Fixtures Compartilhadas ---

@pytest.fixture(scope="function")
def db_session():
    """
    Esta fixture é o coração do isolamento de testes.
    'scope="function"' garante que este código rode para CADA teste.
    """
    # Cria todas as tabelas ANTES de cada teste
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Fornece a sessão para o teste
        yield db
    finally:
        # Executa DEPOIS que o teste termina
        db.close()
        # Destrói todas as tabelas, deixando o banco limpo para o próximo teste
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture que cria um TestClient usando o banco de dados limpo da db_session.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()