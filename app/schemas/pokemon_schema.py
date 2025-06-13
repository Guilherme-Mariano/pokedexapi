from pydantic import BaseModel
from typing import List

# Define o formato de entrada e saída dos objetos

class Stats(BaseModel):
    hp: int
    attack: int
    defense: int

class Pokemon(BaseModel):
    id: int
    name: str
    types: List[str]
    stats: Stats

    class Config:
        orm_mode = True