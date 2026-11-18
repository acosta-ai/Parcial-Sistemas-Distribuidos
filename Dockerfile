FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar requerimientos Python
COPY hsb/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY . .

EXPOSE 8000

CMD ["uvicorn", "hsb.main:app", "--host", "0.0.0.0", "--port", "8000"]
