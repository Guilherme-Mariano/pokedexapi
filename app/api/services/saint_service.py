# app/api/services/santos_service.py

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import saint_model
from app.schemas import saint_schema

def get_all_santos(db: Session) -> List[saint_model.Santos]:
    """
    Recupera todos os Santos do banco de dados, ordenados por nome.
    Retorna uma lista de objetos do modelo SQLAlchemy.
    """
    return db.query(saint_model.Santos).order_by(saint_model.Santos.nome).all()

def get_santo_by_id_or_name(db: Session, id_or_name: str) -> Optional[saint_model.Santos]:
    """
    Busca um Santo específico por ID (se o input for um número) 
    ou por nome (se for texto).
    Retorna um único objeto do modelo SQLAlchemy ou None se não encontrar.
    """
    query = db.query(saint_model.Santos)
    
    # Verifica se o identificador é composto apenas por dígitos
    if id_or_name.isdigit():
        # Se for um número, busca EXCLUSIVAMENTE pelo ID.
        return query.filter(saint_model.Santos.id == int(id_or_name)).first()
    else:
        # Se não for um número, busca EXCLUSIVAMENTE pelo nome (case-insensitive).
        # Usamos 'ilike' para busca case-insensitive.
        return query.filter(saint_model.Santos.nome.ilike(id_or_name)).first()

def create_santo(db: Session, santo: saint_schema.SantosCreate) -> saint_model.Santos:
    """
    Cria um novo registro de Santo no banco de dados.
    Recebe um objeto do schema Pydantic, converte para um modelo SQLAlchemy e o salva.
    """
    # Converte o schema Pydantic em um dicionário
    santo_data = santo.model_dump()
    
    # Cria uma instância do modelo SQLAlchemy usando o dicionário desempacotado (**)
    db_santo = saint_model.Santos(**santo_data)
    
    # Adiciona o novo objeto à sessão do banco de dados
    db.add(db_santo)
    
    # Commita (salva) a transação no banco de dados
    db.commit()
    
    # Atualiza o objeto para obter os dados gerados pelo banco (como o ID)
    db.refresh(db_santo)
    
    return db_santo

def update_santo(db: Session, santo_id: int, santo_update: saint_schema.SantosUpdate) -> Optional[saint_model.Santos]:
    """
    Atualiza um registro de Santo no banco de dados.
    Recebe o ID do santo e um schema Pydantic com os dados a serem atualizados.
    """
    # 1. Busca o santo no banco de dados
    db_santo = db.query(saint_model.Santos).filter(saint_model.Santos.id == santo_id).first()

    if not db_santo:
        return None # Retorna None se o santo não for encontrado

    # 2. Converte o schema Pydantic em um dicionário
    #    'exclude_unset=True' é importante: garante que apenas os campos
    #    que o usuário REALMENTE enviou sejam incluídos no dicionário.
    update_data = santo_update.model_dump(exclude_unset=True)

    # 3. Atualiza os campos do objeto do banco com os dados recebidos
    for key, value in update_data.items():
        setattr(db_santo, key, value)

    # 4. Commita a transação e atualiza o objeto
    db.commit()
    db.refresh(db_santo)
    
    return db_santo

def delete_santo(db: Session, santo_id: int) -> Optional[saint_model.Santos]:
    """
    Deleta um registro de Santo do banco de dados.
    """
    # 1. Busca o santo existente no banco de dados
    db_santo = db.query(saint_model.Santos).filter(saint_model.Santos.id == santo_id).first()

    if not db_santo:
        return None # Retorna None se o santo não for encontrado
    
    # 2. Deleta o objeto da sessão e commita a transação
    db.delete(db_santo)
    db.commit()

    return db_santo # Retorna o objeto deletado para confirmação