# PowerShell script to start FastAPI with PostgreSQL

Write-Host "`n=== Sistema de Servicos - FastAPI ===" -ForegroundColor Cyan

# Verificar se .env existe
if (-Not (Test-Path ".env")) {
    Write-Host "[ERRO] Arquivo .env nao encontrado" -ForegroundColor Red
    Write-Host "Copie .env.example para .env e configure DATABASE_URL com PostgreSQL" -ForegroundColor Yellow
    Write-Host "`nExemplo:" -ForegroundColor Cyan
    Write-Host "  DATABASE_URL=postgresql://postgres:password@localhost:5432/sistema_servicos" -ForegroundColor Gray
    exit 1
}

# Carregar .env
Write-Host "[*] Carregando configuracao de .env..." -ForegroundColor Cyan
$envContent = Get-Content ".env" | Select-String '^DATABASE_URL=' | ForEach-Object { $_.Line -replace '^DATABASE_URL=', '' }

if ($envContent) {
    $env:DATABASE_URL = $envContent
    Write-Host "[OK] DATABASE_URL carregado" -ForegroundColor Green
    Write-Host "     Host: $($envContent.Split('@')[1].Split(':')[0])" -ForegroundColor Gray
} else {
    Write-Host "[ERRO] DATABASE_URL nao encontrado em .env" -ForegroundColor Red
    exit 1
}

Write-Host "`n[*] Iniciando FastAPI com PostgreSQL..." -ForegroundColor Cyan
Write-Host "[*] Acesse: http://localhost:10000" -ForegroundColor Green
Write-Host ""

.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 10000 --reload
