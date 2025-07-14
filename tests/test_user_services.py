# tests/test_user_services.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.api.services import user_service
from app.schemas.user_schema import UserCreate
from app.api.auth import verify_password

# --- Configuração do Banco de Dados de Teste em Memória ---
# (Esta configuração pode ser movida para um arquivo conftest.py para ser reutilizada)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture do Pytest para criar as tabelas e fornecer uma sessão limpa
@pytest.fixture(scope="function")
def db_session():
    # Cria todas as tabelas (incluindo a nova 'users') no BD em memória
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Limpa todas as tabelas após cada teste
        Base.metadata.drop_all(bind=engine)

# --- Início dos Testes do Serviço de Usuário ---

def test_create_user_service(db_session):
    """Testa a criação de um novo usuário e a criptografia da senha."""
    user_in = UserCreate(
        username="testservice",
        email="service@test.com",
        password="password123"
    )
    
    # Chama a função do serviço para criar o usuário
    created_user = user_service.create_user(db=db_session, user=user_in)
    
    # Verifica se o usuário foi criado com os dados corretos
    assert created_user is not None
    assert created_user.username == "testservice"
    assert created_user.email == "service@test.com"
    assert created_user.id is not None # O ID deve ser gerado pelo banco
    
    # Verifica se a senha foi de fato criptografada (não está em texto puro)
    assert created_user.hashed_password != "password123"
    
    # Verifica se a senha original corresponde ao hash gerado
    assert verify_password("password123", created_user.hashed_password)

def test_get_user_by_username_service(db_session):
    """Testa a busca de um usuário pelo username."""
    # Primeiro, cria o usuário que será buscado
    user_in = UserCreate(username="findme", email="find@me.com", password="pwd")
    user_service.create_user(db=db_session, user=user_in)
    
    # Tenta buscar o usuário
    found_user = user_service.get_user_by_username(db=db_session, username="findme")
    
    assert found_user is not None
    assert found_user.username == "findme"

    # Tenta buscar um usuário que não existe
    not_found_user = user_service.get_user_by_username(db=db_session, username="ghost")
    assert not_found_user is None