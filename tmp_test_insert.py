from database import Base, engine, SessionLocal
from models import Cliente

Base.metadata.create_all(bind=engine)
print('tables created')
db = SessionLocal()
try:
    obj = Cliente(nome='Teste', cidade='Cidade')
    db.add(obj)
    db.commit()
    print('insert ok', obj.id)
except Exception as e:
    print('insert failed', type(e).__name__, e)
    db.rollback()
finally:
    db.close()
