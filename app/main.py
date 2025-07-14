from fastapi import FastAPI
from app.api.routes import pokemon
from app.db import database
from app.models import pokemon_model
from app.api.routes import saint
from app.api.routes import auth
# Isso garante que as tabelas do SQLAlchemy sejam criadas quando a aplicação iniciar,
# se elas ainda não existirem.
pokemon_model.Base.metadata.create_all(bind=database.engine)

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

