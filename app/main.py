# app/main.py

from fastapi import FastAPI
from app.db import database

from app.models import saint_model, user_model

from app.api.routes import santos_route
from app.api.routes import auth_route

saint_model.Base.metadata.create_all(bind=database.engine)
user_model.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Enciclopédia de Santos",
    description="Uma API para obter informações sobre Santos Católicos",
    version="1.1.0"
)

app.include_router(santos_route.router)
app.include_router(auth_route.router)

@app.get("/", tags=["Root"])
async def read_root():
    """
    Endpoint que retorna mensagem de boas-vindas.
    """
    return {"message": "Bem-vindo à Enciclopédia de Santos!"}