#!/bin/sh

# O shell irá parar a execução do script se um comando falhar
set -e

# Passo 1: Executa o script Python para criar/popular o banco de dados.
# Garantimos que o banco de dados esteja pronto antes de iniciar a API.
echo "Iniciando a criação do banco de dados..."
python /app/app/db/create_database.py

# Passo 2: Inicia o servidor da aplicação.
# O "exec" substitui o processo do shell pelo processo do uvicorn,
# o que é uma boa prática para o gerenciamento de sinais do Docker.
echo "Iniciando o servidor da API..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000