from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import SessionLocal, engine
from models import Base, Usuario, Cliente, Banco, Servico

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# LOGIN
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.post("/login")
def login(
    usuario: str = Form(...),
    senha: str = Form(...)
):

    db = SessionLocal()

    user = db.query(Usuario).filter(
        Usuario.usuario == usuario,
        Usuario.senha == senha
    ).first()

    if user:
        return RedirectResponse("/dashboard", status_code=303)

    return RedirectResponse("/", status_code=303)

# DASHBOARD
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    db = SessionLocal()

    servicos = db.query(Servico).all()

    total = sum([
        s.valor * s.quantidade
        for s in servicos
    ])

    concluidos = len([
        s for s in servicos
        if s.status == "Concluído"
    ])

    pendentes = len([
        s for s in servicos
        if s.status == "Pendente"
    ])

    cancelados = len([
        s for s in servicos
        if s.status == "Cancelado"
    ])

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total": total,
            "concluidos": concluidos,
            "pendentes": pendentes,
            "cancelados": cancelados
        }
    )

# CLIENTES
@app.get("/clientes", response_class=HTMLResponse)
def clientes(request: Request):

    db = SessionLocal()

    clientes = db.query(Cliente).all()

    return templates.TemplateResponse(
        "clientes.html",
        {
            "request": request,
            "clientes": clientes
        }
    )

@app.post("/clientes")
def salvar_cliente(
    nome: str = Form(...),
    cidade: str = Form(...)
):

    db = SessionLocal()

    novo = Cliente(
        nome=nome,
        cidade=cidade
    )

    db.add(novo)

    db.commit()

    return RedirectResponse("/clientes", status_code=303)

@app.get("/excluir-cliente/{id}")
def excluir_cliente(id: int):

    db = SessionLocal()

    cliente = db.query(Cliente).get(id)

    db.delete(cliente)

    db.commit()

    return RedirectResponse(
        "/clientes",
        status_code=303
    )

@app.get(
    "/editar-cliente/{id}",
    response_class=HTMLResponse
)
def editar_cliente(
    request: Request,
    id: int
):

    db = SessionLocal()

    cliente = db.query(Cliente).get(id)

    return templates.TemplateResponse(
        "editar_cliente.html",
        {
            "request": request,
            "cliente": cliente
        }
    )

@app.post("/editar-cliente/{id}")
def atualizar_cliente(
    id: int,
    nome: str = Form(...),
    cidade: str = Form(...)
):

    db = SessionLocal()

    cliente = db.query(Cliente).get(id)

    cliente.nome = nome
    cliente.cidade = cidade

    db.commit()

    return RedirectResponse(
        "/clientes",
        status_code=303
    )

# CADASTRO USUÁRIO
@app.get("/registrar", response_class=HTMLResponse)
def registrar_page(request: Request):

    return templates.TemplateResponse(
        "registrar.html",
        {"request": request}
    )

@app.post("/registrar")
def registrar_usuario(
    usuario: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...)
):

    db = SessionLocal()

    existe = db.query(Usuario).filter(
        Usuario.usuario == usuario
    ).first()

    if existe:
        return RedirectResponse("/registrar", status_code=303)

    novo = Usuario(
        usuario=usuario,
        email=email,
        senha=senha
    )

    db.add(novo)

    db.commit()

    return RedirectResponse("/", status_code=303)

# BANCOS
@app.get("/bancos", response_class=HTMLResponse)
def bancos(request: Request):

    db = SessionLocal()

    bancos = db.query(Banco).all()

    return templates.TemplateResponse(
        "bancos.html",
        {
            "request": request,
            "bancos": bancos
        }
    )

@app.post("/bancos")
def salvar_banco(
    nome_banco: str = Form(...),
    cidade: str = Form(...),
    valor: float = Form(...),
    descricao: str = Form(...)
):

    db = SessionLocal()

    novo = Banco(
        nome_banco=nome_banco,
        cidade=cidade,
        valor=valor,
        descricao=descricao
    )

    db.add(novo)

    db.commit()

    return RedirectResponse("/bancos", status_code=303)

@app.get("/excluir-banco/{id}")
def excluir_banco(id: int):

    db = SessionLocal()

    banco = db.query(Banco).get(id)

    db.delete(banco)

    db.commit()

    return RedirectResponse(
        "/bancos",
        status_code=303
    )

@app.get(
    "/editar-banco/{id}",
    response_class=HTMLResponse
)
def editar_banco(
    request: Request,
    id: int
):

    db = SessionLocal()

    banco = db.query(Banco).get(id)

    return templates.TemplateResponse(
        "editar_banco.html",
        {
            "request": request,
            "banco": banco
        }
    )

@app.post("/editar-banco/{id}")
def atualizar_banco(
    id: int,
    nome_banco: str = Form(...),
    cidade: str = Form(...),
    valor: float = Form(...),
    descricao: str = Form(...)
):

    db = SessionLocal()

    banco = db.query(Banco).get(id)

    banco.nome_banco = nome_banco
    banco.cidade = cidade
    banco.valor = valor
    banco.descricao = descricao

    db.commit()

    return RedirectResponse(
        "/bancos",
        status_code=303
    )

# SERVIÇOS
@app.get("/servicos", response_class=HTMLResponse)
def servicos(
    request: Request,
    busca: str = "",
    status: str = ""
):

    db = SessionLocal()

    query = db.query(Servico)

    if busca:
        query = query.filter(
            Servico.cliente.contains(busca)
        )

    if status:
        query = query.filter(
            Servico.status == status
        )

    servicos = query.all()

    clientes = db.query(Cliente).all()

    bancos = db.query(Banco).all()

    return templates.TemplateResponse(
        "servicos.html",
        {
            "request": request,
            "servicos": servicos,
            "clientes": clientes,
            "bancos": bancos
        }
    )

@app.post("/servicos")
def salvar_servico(
    cliente: str = Form(...),
    cidade: str = Form(...),
    banco: str = Form(...),
    descricao: str = Form(...),
    valor: float = Form(...),
    quantidade: int = Form(...),
    status: str = Form(...)
):

    db = SessionLocal()

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

    return RedirectResponse("/servicos", status_code=303)

@app.get("/editar-servico/{id}", response_class=HTMLResponse)
def editar_servico(request: Request, id: int):

    db = SessionLocal()

    servico = db.query(Servico).get(id)

    return templates.TemplateResponse(
        "editar_servico.html",
        {
            "request": request,
            "servico": servico
        }
    )

@app.post("/editar-servico/{id}")
def atualizar_servico(
    id: int,
    descricao: str = Form(...),
    status: str = Form(...)
):

    db = SessionLocal()

    servico = db.query(Servico).get(id)

    servico.descricao = descricao

    servico.status = status

    db.commit()

    return RedirectResponse("/servicos", status_code=303)

@app.get("/excluir-servico/{id}")
def excluir_servico(id: int):

    db = SessionLocal()

    servico = db.query(Servico).get(id)

    db.delete(servico)

    db.commit()

    return RedirectResponse("/servicos", status_code=303)