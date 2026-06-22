from fastapi import Depends, FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import threading

from database import Base, engine, SessionLocal, seed_default_user
from models import Usuario, Cliente, Banco, Servico

print('MAIN INICIANDO...')

app = FastAPI()
print('FASTAPI CRIADO')

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

def init_database():
    """Inicializar banco de dados com timeout."""
    try:
        Base.metadata.create_all(bind=engine)
        print('Banco conectado com sucesso')
        seed_default_user()
    except Exception as e:
        print(f'Erro ao conectar ao banco: {e}')


# Tentar inicializar o banco em uma thread separada (background)
# Não aguardar conclusão para não bloquear o startup do app
init_thread = threading.Thread(target=init_database, daemon=True)
init_thread.start()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/', response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, 'login.html', {'request': request})


@app.post('/login')
def login(
    usuario: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(Usuario).filter(
        Usuario.usuario == usuario,
        Usuario.senha == senha
    ).first()

    if user:
        return RedirectResponse('/dashboard', status_code=303)

    return RedirectResponse('/', status_code=303)


@app.get('/dashboard', response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    servicos = db.query(Servico).all()

    total = sum([s.valor * s.quantidade for s in servicos])
    concluidos = len([s for s in servicos if s.status == 'Concluído'])
    pendentes = len([s for s in servicos if s.status == 'Pendente'])
    cancelados = len([s for s in servicos if s.status == 'Cancelado'])

    return templates.TemplateResponse(
        request,
        'dashboard.html',
        {
            'request': request,
            'total': total,
            'concluidos': concluidos,
            'pendentes': pendentes,
            'cancelados': cancelados
        }
    )


@app.get('/clientes', response_class=HTMLResponse)
def clientes(request: Request, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).all()

    return templates.TemplateResponse(
        request,
        'clientes.html',
        {'request': request, 'clientes': clientes}
    )


@app.post('/clientes')
def salvar_cliente(
    nome: str = Form(...),
    cidade: str = Form(...),
    db: Session = Depends(get_db)
):
    novo = Cliente(nome=nome, cidade=cidade)
    db.add(novo)
    db.commit()

    return RedirectResponse('/clientes', status_code=303)


@app.get('/excluir-cliente/{id}')
def excluir_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, id)
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')

    db.delete(cliente)
    db.commit()

    return RedirectResponse('/clientes', status_code=303)


@app.get('/editar-cliente/{id}', response_class=HTMLResponse)
def editar_cliente(request: Request, id: int, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, id)
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')

    return templates.TemplateResponse(
        request,
        'editar_cliente.html',
        {'request': request, 'cliente': cliente}
    )


@app.post('/editar-cliente/{id}')
def atualizar_cliente(
    id: int,
    nome: str = Form(...),
    cidade: str = Form(...),
    db: Session = Depends(get_db)
):
    cliente = db.get(Cliente, id)
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')

    cliente.nome = nome
    cliente.cidade = cidade
    db.commit()

    return RedirectResponse('/clientes', status_code=303)


@app.get('/registrar', response_class=HTMLResponse)
def registrar_page(request: Request):
    return templates.TemplateResponse(request, 'registrar.html', {'request': request})


@app.post('/registrar')
def registrar_usuario(
    usuario: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    existe = db.query(Usuario).filter(Usuario.usuario == usuario).first()
    if existe:
        return RedirectResponse('/registrar', status_code=303)

    novo = Usuario(usuario=usuario, email=email, senha=senha)
    db.add(novo)
    db.commit()

    return RedirectResponse('/', status_code=303)


@app.get('/bancos', response_class=HTMLResponse)
def bancos(request: Request, db: Session = Depends(get_db)):
    bancos = db.query(Banco).all()
    return templates.TemplateResponse(request, 'bancos.html', {'request': request, 'bancos': bancos})


@app.post('/bancos')
def salvar_banco(
    nome_banco: str = Form(...),
    cidade: str = Form(...),
    valor: float = Form(...),
    descricao: str = Form(...),
    db: Session = Depends(get_db)
):
    novo = Banco(nome_banco=nome_banco, cidade=cidade, valor=valor, descricao=descricao)
    db.add(novo)
    db.commit()

    return RedirectResponse('/bancos', status_code=303)


@app.get('/excluir-banco/{id}')
def excluir_banco(id: int, db: Session = Depends(get_db)):
    banco = db.get(Banco, id)
    if banco is None:
        raise HTTPException(status_code=404, detail='Banco não encontrado')

    db.delete(banco)
    db.commit()

    return RedirectResponse('/bancos', status_code=303)


@app.get('/editar-banco/{id}', response_class=HTMLResponse)
def editar_banco(request: Request, id: int, db: Session = Depends(get_db)):
    banco = db.get(Banco, id)
    if banco is None:
        raise HTTPException(status_code=404, detail='Banco não encontrado')

    return templates.TemplateResponse(request, 'editar_banco.html', {'request': request, 'banco': banco})


@app.post('/editar-banco/{id}')
def atualizar_banco(
    id: int,
    nome_banco: str = Form(...),
    cidade: str = Form(...),
    valor: float = Form(...),
    descricao: str = Form(...),
    db: Session = Depends(get_db)
):
    banco = db.get(Banco, id)
    if banco is None:
        raise HTTPException(status_code=404, detail='Banco não encontrado')

    banco.nome_banco = nome_banco
    banco.cidade = cidade
    banco.valor = valor
    banco.descricao = descricao
    db.commit()

    return RedirectResponse('/bancos', status_code=303)


@app.get('/servicos', response_class=HTMLResponse)
def servicos(
    request: Request,
    busca: str = '',
    status_filter: str = '',
    db: Session = Depends(get_db)
):
    query = db.query(Servico)
    if busca:
        query = query.filter(Servico.cliente.contains(busca))
    if status_filter:
        query = query.filter(Servico.status == status_filter)

    servicos = query.all()
    clientes = db.query(Cliente).all()
    bancos = db.query(Banco).all()

    return templates.TemplateResponse(
        request,
        'servicos.html',
        {'request': request, 'servicos': servicos, 'clientes': clientes, 'bancos': bancos}
    )


@app.post('/servicos')
def salvar_servico(
    cliente: str = Form(...),
    cidade: str = Form(...),
    banco: str = Form(...),
    descricao: str = Form(...),
    valor: float = Form(...),
    quantidade: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    novo = Servico(
        cliente=cliente,
        cidade=cidade,
        banco=banco,
        descricao=descricao,
        valor=valor,
        quantidade=quantidade,
        status=status
    )
    db.add(novo)
    db.commit()

    return RedirectResponse('/servicos', status_code=303)


@app.get('/editar-servico/{id}', response_class=HTMLResponse)
def editar_servico(request: Request, id: int, db: Session = Depends(get_db)):
    servico = db.get(Servico, id)
    if servico is None:
        raise HTTPException(status_code=404, detail='Serviço não encontrado')

    return templates.TemplateResponse(request, 'editar_servico.html', {'request': request, 'servico': servico})


@app.post('/editar-servico/{id}')
def atualizar_servico(
    id: int,
    descricao: str = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    servico = db.get(Servico, id)
    if servico is None:
        raise HTTPException(status_code=404, detail='Serviço não encontrado')

    servico.descricao = descricao
    servico.status = status
    db.commit()

    return RedirectResponse('/servicos', status_code=303)


@app.get('/excluir-servico/{id}')
def excluir_servico(id: int, db: Session = Depends(get_db)):
    servico = db.get(Servico, id)
    if servico is None:
        raise HTTPException(status_code=404, detail='Serviço não encontrado')

    db.delete(servico)
    db.commit()

    return RedirectResponse('/servicos', status_code=303)
