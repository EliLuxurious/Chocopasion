# ── Imagen base ────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Metadatos
LABEL maintainer="Chocopasión Dev Team"
LABEL description="Aplicación Flask para gestión de producción y ventas"

# Evitar prompts interactivos durante el build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ── Dependencias del sistema ────────────────────────────────────────────────────
# Necesarias para mysql-connector-python y reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libssl-dev \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Directorio de trabajo ────────────────────────────────────────────────────────
WORKDIR /app

# ── Dependencias Python ─────────────────────────────────────────────────────────
# Copiamos primero solo requirements para aprovechar la caché de capas Docker
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ── Código fuente ────────────────────────────────────────────────────────────────
COPY . .

# ── Puerto expuesto ──────────────────────────────────────────────────────────────
EXPOSE 5000

# ── Health check ─────────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# ── Comando de arranque ──────────────────────────────────────────────────────────
CMD ["python", "infrastructure/database.py"]
