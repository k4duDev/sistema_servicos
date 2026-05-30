# Setup PostgreSQL para Sistema de Servicos

## Windows

### 1. Instalar PostgreSQL
- Download: https://www.postgresql.org/download/windows/
- Instalar com as opcoes padrao
- Lembrar da senha do usuario `postgres`

### 2. Criar banco de dados
```cmd
# Abrir Command Prompt ou PowerShell
# Conectar ao PostgreSQL
psql -U postgres

# Dentro do psql:
CREATE DATABASE sistema_servicos;
```

### 3. Configurar .env
```
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/sistema_servicos
```

### 4. Iniciar o app
```powershell
.\start.ps1
```

---

## Linux (Ubuntu/Debian)

### 1. Instalar PostgreSQL
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Criar banco de dados
```bash
# Conectar como usuario postgres
sudo -u postgres psql

# Dentro do psql:
CREATE DATABASE sistema_servicos;
CREATE USER usuario WITH PASSWORD 'senha';
ALTER ROLE usuario SET client_encoding TO 'utf8';
ALTER ROLE usuario SET default_transaction_isolation TO 'read committed';
ALTER ROLE usuario SET default_transaction_deferrable TO on;
ALTER ROLE usuario SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE sistema_servicos TO usuario;
```

### 3. Configurar .env
```
DATABASE_URL=postgresql://usuario:senha@localhost:5432/sistema_servicos
```

### 4. Iniciar o app
```bash
bash start.sh
```

---

## macOS

### 1. Instalar PostgreSQL com Homebrew
```bash
brew install postgresql
brew services start postgresql
```

### 2. Criar banco de dados
```bash
createdb sistema_servicos
```

### 3. Configurar .env
```
DATABASE_URL=postgresql://usuario_mac:password@localhost:5432/sistema_servicos
```

### 4. Iniciar o app
```bash
bash start.sh
```

---

## Testar a conexao

```python
from sqlalchemy import text
from database import engine

with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print(f"Conectado ao PostgreSQL! Resultado: {result.scalar()}")
```

---

## Troubleshooting

### "FATAL: role 'postgres' does not exist"
- No Windows: Usar usuario `postgres` (padr??o)
- No Linux: Usar `sudo -u postgres psql`

### "Connection refused"
- Verificar se PostgreSQL esta rodando:
  - Windows: Services > postgresql-x64-XX
  - Linux: `sudo systemctl status postgresql`
  - macOS: `brew services list`

### "password authentication failed"
- Verificar usuario/senha em DATABASE_URL
- Testar conexao direta: `psql -U postgres -h localhost`

### "Database 'sistema_servicos' does not exist"
- Criar o banco: `createdb sistema_servicos` (Linux/macOS) ou via psql (Windows)

---

## Proximos passos

1. Copiar `.env.example` para `.env`
2. Configurar DATABASE_URL com credenciais PostgreSQL
3. Executar `start.ps1` ou `start.sh`
4. Acessar http://localhost:10000
