# Estágio 1: Builder - Instala dependências e prepara o ambiente
FROM python:3.11-slim as builder

# Define o diretório de trabalho
WORKDIR /app

# Cria um usuário e grupo não-root para a aplicação
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instala dependências (usando cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Estágio 2: Final - Cria a imagem final, leve e segura
FROM python:3.11-slim as final

# Define o diretório de trabalho
WORKDIR /app

# Copia o usuário não-root criado no estágio anterior
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group

# Copia as dependências instaladas do estágio "builder"
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copia APENAS o código da aplicação necessário para a pasta de trabalho
# Note que estamos copiando o conteúdo da pasta 'app' local para a pasta 'app' no contêiner
COPY ./app /app/app

# Garante que o usuário não-root seja o dono dos arquivos da aplicação
RUN chown -R appuser:appuser /app

# Muda para o usuário não-root
USER appuser

# Expõe a porta que a aplicação vai rodar
EXPOSE 8000

# Comando para iniciar o servidor, apontando para o local correto do código
# Python path: /app, comando: uvicorn app.main:app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]