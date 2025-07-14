from datetime import date
from pydantic import BaseModel, ConfigDict

# Entrada e saída dos objetos que representarão o objeto santo

class SantosBase(BaseModel):
    nome: str
    protecao: str
    festa_liturgica: date
    veneracao: str
    local_de_nascimento: str
    data_de_nascimento: date 
    data_de_morte: date
    historia: str

# Herda de SantosBase e é usado para validar os dados de entrada (POST)
class SantosCreate(SantosBase):
    # Está vazio ( pass ) porque a classe mãe SantosBase já contém todas as informações necessárias
    # para a validação do POST
    pass

class Santos(SantosBase):
    # Adiciona o campo 'id' que não está no schema base
    id: int

    # Agregação do pydantic ao sqlalchemy
    # No caso estamos convertendo o objeto retornado pelo sql a um dicionario tipo dados['chave']
    model_config = ConfigDict(from_attributes=True)


    