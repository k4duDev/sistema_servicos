import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{Path(__file__).parent / 'banco.db'}"
    print("DATABASE_URL não encontrada. Usando fallback local SQLite.")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # PostgreSQL: adicionar timeout para evitar penduração indefinida
    connect_args["connect_timeout"] = 5

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=not DATABASE_URL.startswith("sqlite"),
    pool_recycle=300,
    echo=True
)

if not DATABASE_URL.startswith("sqlite"):
    # Nota: o timeout foi configurado em connect_args acima
    # Não testamos conexão aqui para evitar penduração
    pass

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()