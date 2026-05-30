#!/bin/bash

echo "Iniciando Sistema de Servicos..."

uvicorn main:app --host 0.0.0.0 --port $PORT