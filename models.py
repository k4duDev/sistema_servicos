from sqlalchemy import Column, Integer, String, Float
from database import Base

# LOGIN
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    usuario = Column(String, unique=True)

    email = Column(String)

    senha = Column(String)

# CLIENTES
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    cidade = Column(String)

# BANCOS
class Banco(Base):
    __tablename__ = "bancos"

    id = Column(Integer, primary_key=True, index=True)
    nome_banco = Column(String)
    cidade = Column(String)
    valor = Column(Float)
    descricao = Column(String)

# SERVIÇOS
class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)

    cliente = Column(String)

    cidade = Column(String)

    banco = Column(String)

    descricao = Column(String)

    valor = Column(Float)

    quantidade = Column(Integer)

    status = Column(String)