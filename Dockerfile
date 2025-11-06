# ===============================================
# DOCKERFILE PARA CAUDALIA - EASYPANEL
# ===============================================
# Sistema de Deploy - IdeasDevOps
# Basado en deploy-system-for-easypanel
# Aplicación: Caudalia - Extractor de Caudalímetros
# 
# Arquitectura:
# - Backend Flask: API para procesar imágenes
# - Tesseract OCR: Reconocimiento de texto
# - OpenCV: Procesamiento de imágenes
# - EasyPanel gestiona: nginx, supervisor, puerto 80
# ===============================================

# Etapa 1: Builder (para optimizar tamaño final)
FROM python:3.11-slim as builder

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /build

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# ===============================================
# Etapa 2: Runtime
# ===============================================
FROM python:3.11-slim

# ===============================================
# METADATOS DE LA APLICACIÓN
# ===============================================
ARG APP_NAME="caudalia"
ARG APP_VERSION="1.0.0"
ARG APP_DESCRIPTION="Sistema de extracción de datos de caudalímetros usando OCR y detección de áreas rojas"
LABEL maintainer="IdeasDevOps"
LABEL app.name="${APP_NAME}"
LABEL app.version="${APP_VERSION}"
LABEL app.description="${APP_DESCRIPTION}"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=5000

# ===============================================
# INSTALACIÓN DE DEPENDENCIAS DEL SISTEMA
# ===============================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Tesseract OCR y idiomas
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    # Dependencias de OpenCV
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Utilidades
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# ===============================================
# CREACIÓN DE DIRECTORIOS
# ===============================================
# Crear directorios en /data (donde estarán los volúmenes)
RUN mkdir -p \
    /data/uploads \
    /data/logs \
    /data/cache \
    /app \
    && chmod -R 755 /data

# ===============================================
# CONFIGURACIÓN DE USUARIO
# ===============================================
# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    chown -R appuser:appuser /app /data

# ===============================================
# COPIA DE DEPENDENCIAS Y CÓDIGO
# ===============================================
# Copiar dependencias Python desde builder
COPY --from=builder /root/.local /root/.local

# Establecer directorio de trabajo
WORKDIR /app

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# ===============================================
# CONFIGURACIÓN DE PERMISOS
# ===============================================
RUN chmod +x iniciar_servidor.sh ejecutar.sh verificar_requisitos.sh || true

# ===============================================
# CAMBIAR A USUARIO NO-ROOT
# ===============================================
USER appuser

# ===============================================
# PUERTO Y HEALTH CHECK
# ===============================================
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# ===============================================
# COMANDO DE INICIO
# ===============================================
# Usar gunicorn para producción (más robusto que Flask dev server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]

