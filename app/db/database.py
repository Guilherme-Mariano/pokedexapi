# app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# URL atualizada
DATABASE_URL = "sqlite:///./app/db/saintdoom.db"

# 'engine'
engine = create_engine(
    DATABASE_URL,
    # Este argumento é essencial para o SQLite em aplicações com múltiplas threads.
    connect_args={"check_same_thread": False} 
)

# Criando a classe "fábrica" de sessões. A convenção é chamá-la de SessionLocal.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crie a Base para os seus modelos declarativos.
Base = declarative_base()

# Matendo get_db
# garante que cada requisição tenha sua própria sessão e que ela seja fechada.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()