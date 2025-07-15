# tests/test_user_services.py

from app.api.services import user_service
from app.schemas.user_schema import UserCreate
from app.api.core.security import verify_password


def test_create_user_service(db_session):
    """Testa a criação de um novo usuário e a criptografia da senha."""
    user_in = UserCreate(
        username="testservice",
        email="service@test.com",
        password="password123"
    )
    
    created_user = user_service.create_user(db=db_session, user=user_in)
    
    assert created_user is not None
    assert created_user.username == "testservice"
    assert created_user.hashed_password != "password123"
    assert verify_password("password123", created_user.hashed_password)

def test_get_user_by_username_service(db_session):
    """Testa a busca de um usuário pelo username."""
    user_in = UserCreate(username="findme", email="find@me.com", password="pwd")
    user_service.create_user(db=db_session, user=user_in)
    
    found_user = user_service.get_user_by_username(db=db_session, username="findme")
    assert found_user is not None
    assert found_user.username == "findme"

    not_found_user = user_service.get_user_by_username(db=db_session, username="ghost")
    assert not_found_user is None