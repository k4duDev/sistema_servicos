from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#DATABASE_URL = "sqlite:///./banco.db"
#DATABASE_URL = "postgresql://usuario:senha@host:5432/banco"
DATABASE_URL = "postgresql://postgres:N4sc1m3nt0@db.ihrwdfyyivctirrymgkq.supabase.co:5432/postgres"

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()