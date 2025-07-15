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

# --- Fixtures Compartilhadas do Pytest ---

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture que cria todas as tabelas antes de cada teste e as destrói depois.
    Garante total isolamento entre os testes.
    """
    # Garante que os modelos foram importados e a Base os conhece
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    Fixture que cria um TestClient e sobrescreve a dependência get_db
    para usar o banco de dados de teste limpo.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()