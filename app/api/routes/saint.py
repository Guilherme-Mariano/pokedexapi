# app/api/routes/santos_route.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

# Importa os componentes específicos dos Santos
from app.api.services import saint_service
from app.schemas import saint_schema

# Importa a dependência do banco de dados
from app.api.dependencies import get_db

# Dependências de autentificação
from app.api import auth # Importe o módulo de autenticação
from app.schemas import user_schema # Importe o schema do usuário

# Cria um novo roteador.
# O 'prefix' garante que todos os endpoints aqui comecem com /santos.
router = APIRouter(
    prefix="/santos",
    tags=["Santos"]
)

@router.get("/", response_model=List[saint_schema.Santos])
def get_all_santos_endpoint(db: Session = Depends(get_db)):
    """
    Recupera todos os Santos cadastrados no banco de dados.
    """
    return saint_service.get_all_santos(db=db)

@router.get("/{id_or_name}", response_model=saint_schema.Santos)
def get_santo_by_id_or_name_endpoint(id_or_name: str, db: Session = Depends(get_db)):
    """
    Busca um Santo específico pelo seu ID numérico ou pelo seu Nome.
    A busca por nome é case-insensitive.
    """
    db_santo = saint_service.get_santo_by_id_or_name(db=db, id_or_name=id_or_name)
    
    # Se o serviço retornar None, significa que o santo não foi encontrado.
    if db_santo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Santo não encontrado"
            #detail="Santo encontrado"
        )
    
    return db_santo

@router.post("/", response_model=saint_schema.Santos, status_code=status.HTTP_201_CREATED)
def create_santo_endpoint(
    santo: saint_schema.SantosCreate, # O corpo (body) da requisição
    db: Session = Depends(get_db)      # A dependência do banco de dados
):
    """
    Cria um novo Santo no banco de dados com as informações fornecidas.
    """
    return saint_service.create_santo(db=db, santo=santo)

@router.patch("/{santo_id}", response_model=saint_schema.Santos)
def update_santo_endpoint(
    santo_id: int,
    santo_data: saint_schema.SantosUpdate, # Usa o novo schema de update
    db: Session = Depends(get_db)
):
    """
    Atualiza parcialmente um Santo existente
    """
    updated_santo = saint_service.update_santo(db=db, santo_id=santo_id, santo_update=santo_data)
    if updated_santo is None:
        raise HTTPException(status_code=404, detail="Santo não encontrado")
    return updated_santo

@router.delete("/{santo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_santo_endpoint(
    santo_id: int,
    db: Session = Depends(get_db)
):
    """
    Deleta um Santo existente
    """
    deleted_santo = saint_service.delete_santo(db=db, santo_id=santo_id)
    if deleted_santo is None:
        raise HTTPException(status_code=404, detail="Santo não encontrado")
    
    # Para o status 204, a resposta não deve ter corpo.
    return Response(status_code=status.HTTP_204_NO_CONTENT)