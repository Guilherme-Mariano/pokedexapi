# app/api/services/user_service.py

from sqlalchemy.orm import Session
from typing import Optional
from app.models import user_model
from app.schemas import user_schema
from app.api.auth import get_password_hash # Importa a função de hashing

def get_user_by_username(db: Session, username: str) -> Optional[user_model.User]:
    """Busca um usuário pelo nome."""
    return db.query(user_model.User).filter(user_model.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[user_model.User]:
    """Busca um usuário pelo e-mail."""
    return db.query(user_model.User).filter(user_model.User.email == email).first()

def create_user(db: Session, user: user_schema.UserCreate) -> user_model.User:
    hashed_password = get_password_hash(user.password)
    db_user = user_model.User(
        username=user.username,
        email=user.email, # Passando o e-mail para o modelo
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user