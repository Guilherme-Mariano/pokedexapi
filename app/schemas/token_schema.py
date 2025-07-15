# app/schemas/token_schema.py

from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """
    Define a estrutura da resposta de login bem-sucedido.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Define a estrutura dos dados (payload) contidos dentro do token JWT.
    """
    username: Optional[str] = None