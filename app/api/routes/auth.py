from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import auth, dependencies
from app.api.services import user_service
from app.schemas import user_schema

router = APIRouter(tags=["Authentication"])

@router.post("/users/", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: user_schema.UserCreate, db: Session = Depends(dependencies.get_db)):
    """Endpoint público para criar um novo usuário."""
    # Verifica se o username já existe
    db_user = user_service.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = user_service.get_user_by_email(db, email=user.email)
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    return user_service.create_user(db=db, user=user)

@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependencies.get_db)
):
    """
    Endpoint de login. Recebe username/password via form data,
    autentica e retorna um token de acesso.
    """
    user = user_service.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.patch("/users/{user_id}", response_model=user_schema.User)
def update_user_endpoint(
    user_id: int,
    user_data: user_schema.UserUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: user_schema.User = Depends(auth.get_current_user)
):
    """Atualiza os dados do próprio usuário. Requer autenticação."""
    # Lógica de Autorização: O ID do usuário logado deve ser o mesmo do usuário a ser alterado.
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não tem permissão para modificar este usuário."
        )

    updated_user = user_service.update_user(db=db, user_id=user_id, user_update=user_data)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return updated_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: user_schema.User = Depends(auth.get_current_user)
):
    """Deleta o próprio usuário. Requer autenticação."""
    # Lógica de Autorização: O ID do usuário logado deve ser o mesmo do usuário a ser deletado.
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não tem permissão para deletar este usuário."
        )

    deleted_user = user_service.delete_user(db=db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return Response(status_code=status.HTTP_204_NO_CONTENT)