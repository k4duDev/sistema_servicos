# Sistema de Serviços

Aplicação FastAPI para gerenciamento de clientes, bancos e serviços com PostgreSQL.

## 🚀 Quick Start

### Pré-requisitos
- Python 3.8+
- PostgreSQL (Supabase ou local)

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar DATABASE_URL

#### Opção A: Arquivo `.env` (recomendado)
```bash
# Copiar .env.example para .env
cp .env.example .env

# Editar .env com suas credenciais PostgreSQL
```

#### Opção B: Variável de ambiente
```bash
# PowerShell
$env:DATABASE_URL = "postgresql://usuario:senha@host:5432/banco"

# Bash
export DATABASE_URL="postgresql://usuario:senha@host:5432/banco"
```

### 3. Executar o servidor

#### Windows (PowerShell)
```powershell
.\start.ps1
```

#### Linux/Mac (Bash)
```bash
bash start.sh
```

#### Manual
```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

O servidor estará disponível em: **http://0.0.0.0:10000**

---

## 🗄️ Banco de Dados

### Supabase (PostgreSQL Cloud)
```
DATABASE_URL=postgresql://postgres:SENHA@db.HASH.supabase.co:5432/postgres?sslmode=require
```

### PostgreSQL Local
```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/sistema_servicos
```

### SQLite (apenas para testes)
```
DATABASE_URL=sqlite:///./banco.db
```

---

## 📁 Estrutura de Arquivos

```
.
├── main.py              # Aplicação FastAPI
├── models.py            # Modelos SQLAlchemy
├── database.py          # Configuração do banco
├── requirements.txt     # Dependências
├── start.sh            # Script de inicialização (Linux/Mac)
├── start.ps1           # Script de inicialização (Windows)
├── .env                # Variáveis de ambiente (gitignore)
├── .env.example        # Exemplo de configuração
├── static/             # Arquivos estáticos (CSS, JS)
└── templates/          # Templates HTML (Jinja2)
```

---

## 🔐 Segurança

- **Nunca commite `.env` com senhas reais**
- Use `.env.example` como modelo
- Mantenha DATABASE_URL seguro em variáveis de ambiente

---

## 📝 Rotas Principais

- `GET /` - Página de login
- `POST /login` - Autenticar
- `GET /dashboard` - Dashboard
- `GET /clientes` - Lista de clientes
- `GET /bancos` - Lista de bancos
- `GET /servicos` - Lista de serviços

---

## ⚠️ Troubleshooting

### "DATABASE_URL não está definida"
- Verifique se `.env` existe ou se a variável de ambiente está exportada

### "Connection timed out"
- Verifique se o host PostgreSQL é acessível
- Teste: `ping host_postgres`
- Confirme a porta (padrão: 5432)

### "FATAL: password authentication failed"
- Verifique usuário e senha em DATABASE_URL
- Tente conectar diretamente: `psql -U usuario -h host -d banco`
