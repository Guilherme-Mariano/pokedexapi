from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

# Estrutura do objeto dentro do sqlite

class Pokemon(Base):
    __tablename__ = "pokemons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hp = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)

    types = relationship("PokemonType", back_populates="pokemon")

class PokemonType(Base):
    __tablename__ = "pokemon_types"

    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String)
    pokemon_id = Column(Integer, ForeignKey("pokemons.id"))

    pokemon = relationship("Pokemon", back_populates="types")