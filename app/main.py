from fastapi import FastAPI
from app.api.routes import pokemon
from app.db import database
from app.models import pokemon_model

# Isso garante que as tabelas do SQLAlchemy sejam criadas quando a aplicação iniciar,
# se elas ainda não existirem.
pokemon_model.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Pokédex API",
    description="Uma API para obter informações sobre Pokémon",
    version="1.1.0"
)

# Inclui o roteador de pokemon na aplicação principal
app.include_router(pokemon.router)

@app.get("/", tags=["Root"])
async def read_root():
    #return {"message": "Bem-vindo à Pokédex API!"}
    return {"message": "Bem-vindo"}