from sqlalchemy import Column, String, Integer, Date
from app.db.database import Base
class Santos(Base):

    __tablename__ = "santos"

    id = Column("id", Integer,primary_key=True, autoincrement = True)
    nome = Column("nome", String)
    protecao = Column("proteção", String)
    festa_liturgica = Column("festa litúrgica", Date)
    veneracao = Column("veneração", String)
    local_de_nascimento = Column("local de nascimento", String)
    data_de_nascimento = Column("data de nascimento", Date)
    data_de_morte = Column("data de morte", Date)
    historia = Column("historia", String)
    atribuicoes = Column("atribuições", String)
    # imagem = Column("imagem", )

    # Sqlalchemy geralmente cuida do init