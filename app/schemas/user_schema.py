# app/schemas/user_schema.py
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr # Facilita a lógica de validação do email

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    """Schema para atualizar um usuário. Todos os campos são opcionais."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None