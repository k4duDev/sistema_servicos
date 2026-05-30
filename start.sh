# #!/bin/bash

# # Bash script to start FastAPI with PostgreSQL

# echo ""
# echo "=== Sistema de Servicos - FastAPI ==="
# echo ""

# # Verificar se .env existe
# if [ ! -f ".env" ]; then
#     echo "[ERRO] Arquivo .env nao encontrado"
#     echo "Copie .env.example para .env e configure DATABASE_URL com PostgreSQL"
#     echo ""
#     echo "Exemplo:"
#     echo "  DATABASE_URL=postgresql://postgres:password@localhost:5432/sistema_servicos"
#     exit 1
# fi

# # Carregar .env
# echo "[*] Carregando configuracao de .env..."
# source .env

# if [ -z "$DATABASE_URL" ]; then
#     echo "[ERRO] DATABASE_URL nao encontrado em .env"
#     exit 1
# else
#     echo "[OK] DATABASE_URL carregado"
# fi

# echo ""
# echo "[*] Iniciando FastAPI com PostgreSQL..."
# echo "[*] Acesse: http://localhost:10000"
# echo ""

# uvicorn main:app --host 0.0.0.0 --port 10000 --reload


#!/bin/bash

echo "Iniciando Sistema de Servicos..."

uvicorn main:app --host 0.0.0.0 --port $PORT