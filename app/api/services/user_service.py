# app/api/services/user_service.py

from sqlalchemy.orm import Session
from typing import Optional
from app.models import user_model
from app.schemas import user_schema
from app.api.core.security import get_password_hash 

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
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: user_schema.UserUpdate) -> Optional[user_model.User]:
    """Atualiza um usuário."""
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    # Se a senha estiver sendo atualizada, ela precisa passar por hash
    if "password" in update_data:
        db_user.hashed_password = get_password_hash(update_data["password"])
        del update_data["password"] # Remove para não tentar atribuir duas vezes

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> Optional[user_model.User]:
    """Deleta um usuário."""
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user