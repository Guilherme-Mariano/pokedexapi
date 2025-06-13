# app/api/services/pokemon_service.py

from sqlalchemy.orm import Session, joinedload
from app.models import pokemon_model
from app.schemas import pokemon_schema
from typing import List, Optional

def get_all_pokemon(db: Session) -> List[pokemon_schema.Pokemon]:
    """Recupera todos os Pokémon com seus tipos de forma otimizada."""
    pokemons_db = db.query(pokemon_model.Pokemon).options(joinedload(pokemon_model.Pokemon.types)).order_by(pokemon_model.Pokemon.id).all()

    result = []
    for p in pokemons_db:
        stats = pokemon_schema.Stats(hp=p.hp, attack=p.attack, defense=p.defense)
        types = [t.type_name for t in p.types]
        result.append(pokemon_schema.Pokemon(id=p.id, name=p.name, types=types, stats=stats))
    return result

def get_pokemon_by_id_or_name(db: Session, id_or_name: str) -> Optional[pokemon_schema.Pokemon]:
    """
    Busca um Pokémon por ID (se o input for um número) ou por nome (se for texto).
    Esta nova versão é mais explícita e robusta.
    """
    
    query = db.query(pokemon_model.Pokemon).options(joinedload(pokemon_model.Pokemon.types))
    
    # Verifica se o identificador é composto apenas por dígitos
    if id_or_name.isdigit():
        # Se for um número, busca EXCLUSIVAMENTE pelo ID.
        pokemon_db = query.filter(pokemon_model.Pokemon.id == int(id_or_name)).first()
    else:
        # Se não for um número, busca EXCLUSIVAMENTE pelo nome (case-insensitive).
        pokemon_db = query.filter(pokemon_model.Pokemon.name.ilike(id_or_name)).first()

    if pokemon_db:
        stats = pokemon_schema.Stats(hp=pokemon_db.hp, attack=pokemon_db.attack, defense=pokemon_db.defense)
        types = [t.type_name for t in pokemon_db.types]
        return pokemon_schema.Pokemon(id=pokemon_db.id, name=pokemon_db.name, types=types, stats=stats)

    return None