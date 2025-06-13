from app.db.database import SessionLocal

# Injeção de dependências do fastapi
# Aqui o fastapi injeta a funcionalidade de acesso ao banco de dados em cada rota
# Ocorre injeção nas rotas entretanto quanto aos services a funcionalidade está sendo
# passada como argumento


# Aqui é declarado get_db e em routes/pokemon.py observaremos que db: Session = Depends(get_db)
# está presente nas funções que são executadas quando acessamos alguma rota
# Todas as funções do service possuem db: Session como parâmetro
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()