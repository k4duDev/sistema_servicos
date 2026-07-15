import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
FALLBACK_TO_SQLITE = os.getenv("FALLBACK_TO_SQLITE", "true").strip().lower() in ("1", "true", "yes")

fallback_db_path = Path(__file__).parent / "banco.db"


def get_sqlite_url() -> str:
    return f"sqlite:///{fallback_db_path.as_posix()}"


def is_postgres_url(url: str) -> bool:
    try:
        parsed = make_url(url)
        return parsed.drivername.startswith("postgres")
    except Exception:
        return False


def normalize_database_url(url: str) -> str:
    if url and is_postgres_url(url):
        if "sslmode=" not in url.lower():
            if "?" in url:
                return f"{url}&sslmode=require"
            return f"{url}?sslmode=require"
    return url


if DATABASE_URL:
    DATABASE_URL = normalize_database_url(DATABASE_URL)


def create_db_engine(url: str):
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    else:
        connect_args["connect_timeout"] = 5

    return create_engine(
        url,
        connect_args=connect_args,
        pool_pre_ping=not url.startswith("sqlite"),
        pool_recycle=300,
        echo=True,
    )


def try_postgres_connection(url: str):
    engine = create_db_engine(url)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Conexão PostgreSQL bem-sucedida.")
        return engine
    except Exception as error:
        print(f"Falha ao conectar PostgreSQL ({url}): {error}")
        return None


if DATABASE_URL:
    print("DATABASE_URL carregada do ambiente:", DATABASE_URL)
else:
    print("DATABASE_URL não encontrada no ambiente.")


engine = None
if not DATABASE_URL:
    DATABASE_URL = get_sqlite_url()
    print("Usando fallback local SQLite:", DATABASE_URL)
    engine = create_db_engine(DATABASE_URL)
else:
    if DATABASE_URL.startswith("sqlite"):
        engine = create_db_engine(DATABASE_URL)
    elif is_postgres_url(DATABASE_URL):
        engine = try_postgres_connection(DATABASE_URL)
        if engine is None:
            if FALLBACK_TO_SQLITE:
                DATABASE_URL = get_sqlite_url()
                print("Usando fallback local SQLite porque o PostgreSQL não está disponível:", DATABASE_URL)
                engine = create_db_engine(DATABASE_URL)
            else:
                raise RuntimeError(
                    "Não foi possível conectar ao Supabase. "
                    "Defina FALLBACK_TO_SQLITE=true para usar SQLite local, ou corrija a conexão Supabase."
                )
    else:
        engine = create_db_engine(DATABASE_URL)

if engine is None:
    raise RuntimeError("Falha ao inicializar a engine de banco de dados.")


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def seed_default_user():
    """Criar usuário admin padrão se não existir."""
    db = SessionLocal()
    try:
        from models import Usuario

        usuario_existe = db.query(Usuario).filter(Usuario.usuario == "admin").first()

        if not usuario_existe:
            admin = Usuario(usuario="admin", email="admin@sistema.com", senha="123")
            db.add(admin)
            db.commit()
            print("✓ Usuário admin criado com sucesso (usuário: admin, senha: 123)")
        else:
            print("✓ Usuário admin já existe")
    except Exception as e:
        print(f"Erro ao criar usuário admin: {e}")
        db.rollback()
    finally:
        db.close()

