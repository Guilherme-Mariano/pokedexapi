from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.services import pokemon_service
from app.schemas import pokemon_schema
from app.api.dependencies import get_db

router = APIRouter()

@router.get('/pokemon', response_model=List[pokemon_schema.Pokemon])
async def get_all_pokemon_endpoint(db: Session = Depends(get_db)):
    return pokemon_service.get_all_pokemon(db)

@router.get('/pokemon/{id_or_name}', response_model=pokemon_schema.Pokemon)
async def get_pokemon_by_id_or_name_endpoint(id_or_name: str, db: Session = Depends(get_db)):
    pokemon = pokemon_service.get_pokemon_by_id_or_name(db, id_or_name)
    if pokemon:
        return pokemon
    raise HTTPException(status_code=404, detail='Pokemon Não Encontrado')