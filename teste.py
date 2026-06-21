from sqlalchemy import create_engine, text

DATABASE_URL = "SUA_URL_COMPLETA"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print(conn.execute(text("select now()")).fetchone())
    