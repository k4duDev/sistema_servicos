from fastapi import Depends, FastAPI, Request, Form, HTTPException
from typing import Optional
from urllib.parse import parse_qsl
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import threading

from database import Base, engine, SessionLocal, initialize_database
from models import Usuario, Cliente, Banco, Servico

print('MAIN INICIANDO...')

app = FastAPI()
print('FASTAPI CRIADO')

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

@app.on_event("startup")
def startup_event():
    initialize_database()


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
async def salvar_cliente(
    request: Request,
    db: Session = Depends(get_db),
    nome: Optional[str] = Form(None),
    cidade: Optional[str] = Form(None),
):
    if request.headers.get('content-type', '').startswith('application/json'):
        data = await request.json()
        nome = data.get('nome')
        cidade = data.get('cidade')
    elif request.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
        body = await request.body()
        parsed = dict(parse_qsl(body.decode('utf-8')))
        nome = parsed.get('nome', nome)
        cidade = parsed.get('cidade', cidade)
    else:
        form = await request.form()
        nome = form.get('nome', nome)
        cidade = form.get('cidade', cidade)

    if not nome or not cidade:
        raise HTTPException(status_code=422, detail='Nome e cidade são obrigatórios')

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
async def atualizar_cliente(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    nome: Optional[str] = Form(None),
    cidade: Optional[str] = Form(None),
):
    if request.headers.get('content-type', '').startswith('application/json'):
        data = await request.json()
        nome = data.get('nome')
        cidade = data.get('cidade')
    elif request.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
        body = await request.body()
        parsed = dict(parse_qsl(body.decode('utf-8')))
        nome = parsed.get('nome', nome)
        cidade = parsed.get('cidade', cidade)
    else:
        form = await request.form()
        nome = form.get('nome', nome)
        cidade = form.get('cidade', cidade)

    cliente = db.get(Cliente, id)
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')

    if not nome or not cidade:
        raise HTTPException(status_code=422, detail='Nome e cidade são obrigatórios')

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
async def salvar_banco(
    request: Request,
    db: Session = Depends(get_db),
    nome_banco: Optional[str] = Form(None),
    cidade: Optional[str] = Form(None),
    valor: Optional[float] = Form(None),
    descricao: Optional[str] = Form(None),
):
    if request.headers.get('content-type', '').startswith('application/json'):
        data = await request.json()
        nome_banco = data.get('nome_banco')
        cidade = data.get('cidade')
        valor = data.get('valor')
        descricao = data.get('descricao')
    elif request.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
        body = await request.body()
        parsed = dict(parse_qsl(body.decode('utf-8')))
        nome_banco = parsed.get('nome_banco', nome_banco)
        cidade = parsed.get('cidade', cidade)
        valor = parsed.get('valor', valor)
        descricao = parsed.get('descricao', descricao)
    else:
        form = await request.form()
        nome_banco = form.get('nome_banco', nome_banco)
        cidade = form.get('cidade', cidade)
        valor = form.get('valor', valor)
        descricao = form.get('descricao', descricao)

    if not nome_banco or not cidade or valor is None or not descricao:
        raise HTTPException(status_code=422, detail='Todos os campos do banco são obrigatórios')

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
async def atualizar_banco(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    nome_banco: Optional[str] = Form(None),
    cidade: Optional[str] = Form(None),
    valor: Optional[float] = Form(None),
    descricao: Optional[str] = Form(None),
):
    if request.headers.get('content-type', '').startswith('application/json'):
        data = await request.json()
        nome_banco = data.get('nome_banco')
        cidade = data.get('cidade')
        valor = data.get('valor')
        descricao = data.get('descricao')
    elif request.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
        body = await request.body()
        parsed = dict(parse_qsl(body.decode('utf-8')))
        nome_banco = parsed.get('nome_banco', nome_banco)
        cidade = parsed.get('cidade', cidade)
        valor = parsed.get('valor', valor)
        descricao = parsed.get('descricao', descricao)
    else:
        form = await request.form()
        nome_banco = form.get('nome_banco', nome_banco)
        cidade = form.get('cidade', cidade)
        valor = form.get('valor', valor)
        descricao = form.get('descricao', descricao)

    banco = db.get(Banco, id)
    if banco is None:
        raise HTTPException(status_code=404, detail='Banco não encontrado')

    if not nome_banco or not cidade or valor is None or not descricao:
        raise HTTPException(status_code=422, detail='Todos os campos do banco são obrigatórios')

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
    status: str = '',
    db: Session = Depends(get_db)
):
    query = db.query(Servico)
    if busca:
        query = query.filter(Servico.cliente.contains(busca))
    if status:
        query = query.filter(Servico.status == status)

    servicos = query.all()
    clientes = db.query(Cliente).all()
    bancos = db.query(Banco).all()

    return templates.TemplateResponse(
        request,
        'servicos.html',
        {
            'request': request,
            'servicos': servicos,
            'clientes': clientes,
            'bancos': bancos,
            'busca': busca,
            'status': status,
        }
    )


@app.post('/servicos')
async def salvar_servico(
    request: Request,
    db: Session = Depends(get_db),
    cliente: Optional[str] = Form(None),
    cidade: Optional[str] = Form(None),
    banco: Optional[str] = Form(None),
    descricao: Optional[str] = Form(None),
    valor: Optional[float] = Form(None),
    quantidade: Optional[int] = Form(None),
    status: Optional[str] = Form(None),
):
    if request.headers.get('content-type', '').startswith('application/json'):
        data = await request.json()
        cliente = data.get('cliente')
        cidade = data.get('cidade')
        banco = data.get('banco')
        descricao = data.get('descricao')
        valor = data.get('valor')
        quantidade = data.get('quantidade')
        status = data.get('status')
    elif request.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
        body = await request.body()
        parsed = dict(parse_qsl(body.decode('utf-8')))
        cliente = parsed.get('cliente', cliente)
        cidade = parsed.get('cidade', cidade)
        banco = parsed.get('banco', banco)
        descricao = parsed.get('descricao', descricao)
        valor = parsed.get('valor', valor)
        quantidade = parsed.get('quantidade', quantidade)
        status = parsed.get('status', status)
    else:
        form = await request.form()
        cliente = form.get('cliente', cliente)
        cidade = form.get('cidade', cidade)
        banco = form.get('banco', banco)
        descricao = form.get('descricao', descricao)
        valor = form.get('valor', valor)
        quantidade = form.get('quantidade', quantidade)
        status = form.get('status', status)

    if not cliente or not cidade or not banco or not descricao or valor is None or quantidade is None or not status:
        raise HTTPException(status_code=422, detail='Todos os campos de serviço são obrigatórios')

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
