from sqlalchemy import create_engine, Column, String, Integer, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# # Inicia a comunicação com o db

# DATABASE_URL = "sqlite:///./app/db/pokedex.sqlite"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# MARK: implementacao do banco dos santos

db = create_engine("sqlite:///./app/db/saintdoom.db")
Session = sessionmaker(autocommit = False, autoflush = False, bind = db)
mySession = Session()  

Base = declarative_base()
Base.metadata.create_all(db)


