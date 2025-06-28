from sqlalchemy import Column, String, Integer, Date

class Santos(Base):

    __tablename__ = "santos"

    id = Column("id", Integer, autoincrement = True)
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

    def __init__ (self, id, nome, protecao, festa_liturgica, veneracao, local_de_nascimento, data_de_nascimento, data_de_morte, historia, atribuicoes):
        self.id = id 
        self.nome = nome
        self.protecao = protecao
        self.festa_liturgica = festa_liturgica
        self.veneracao = veneracao
        self.local_de_nascimento = local_de_nascimento
        self.data_de_nascimento = data_de_nascimento
        self.data_de_morte = data_de_morte
        self.historia = historia
        self.atribuicoes = atribuicoes