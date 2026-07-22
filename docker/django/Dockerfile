FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser

# Instalar dependencias sistema + Node
RUN apt-get update \
    && apt-get install -y gcc libpq-dev curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# ✅ Instalar npm deps de tailwind
COPY theme/static_src/package*.json ./theme/static_src/

WORKDIR /app/theme/static_src

RUN npm install

# Volver al proyecto
WORKDIR /app

# Copiar proyecto
COPY . .

RUN chown -R appuser:appuser /app

USER appuser

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]