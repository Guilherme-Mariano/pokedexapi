from fastapi import FastAPI
from app.db import database
from app.api.routes import saint
from app.api.routes import auth
# Isso garante que as tabelas do SQLAlchemy sejam criadas quando a aplicação iniciar,
# se elas ainda não existirem.

app = FastAPI(
    title="Enciclopédia de Santos",
    description="Uma API para obter informações sobre Santos Católicos",
    version="1.1.0"
)

app.include_router(saint.router) 
app.include_router(auth.router)
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo"}

