from sqlalchemy import Column, String, Integer

class Usuarios(Base):

    __tablename__ = "usuarios"

    id = Column("id", Integer, autoincrement = True)
    nome_de_usuario = Column("nome de usuário", String) 
    senha = Column("senha", String)
    hash_senha = Column("hash senha", String)
    email = Column("email", String)

    def __init__ (self, id, nome_de_usuario, senha, hash_senha, email):
        self.id = id
        self.nome_de_usuario = nome_de_usuario
        self.senha = senha
        self.hash_senha = hash_senha
        self.email = email