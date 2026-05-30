import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Tentar carregar .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "\n[ERRO] DATABASE_URL nao esta definida.\n"
        "Configure a variavel de ambiente DATABASE_URL ou crie um arquivo .env\n\n"
        "Exemplo para PostgreSQL local:\n"
        "  export DATABASE_URL='postgresql://postgres:password@localhost:5432/sistema_servicos'\n\n"
        "Ou copie .env.example para .env e edite com suas credenciais PostgreSQL"
    )

if not DATABASE_URL.startswith('postgresql'):
    raise RuntimeError(
        "\n[ERRO] Este projeto requer PostgreSQL!\n"
        f"DATABASE_URL nao eh PostgreSQL: {DATABASE_URL[:50]}...\n\n"
        "Atualize .env com um URL PostgreSQL valido:\n"
        "  postgresql://usuario:senha@host:5432/banco"
    )

try:
    engine = create_engine(DATABASE_URL, echo=False)
except Exception as e:
    raise RuntimeError(f"[ERRO] Falha ao criar engine SQLAlchemy:\n{e}")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()