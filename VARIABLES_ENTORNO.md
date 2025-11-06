# 🔧 Variables de Entorno - Caudalia

Documentación completa de las variables de entorno necesarias para configurar Caudalia.

## 📋 Variables Esenciales (Requeridas)

Estas variables son **necesarias** para el funcionamiento básico:

| Variable | Valor por Defecto | Descripción | Requerida |
|----------|-------------------|-------------|-----------|
| `FLASK_APP` | `app.py` | Archivo principal de Flask | ✅ |
| `FLASK_ENV` | `production` | Entorno de ejecución (production/development) | ✅ |
| `PORT` | `5000` | Puerto donde escucha el servidor | ✅ |
| `UPLOAD_FOLDER` | `/data/uploads` | Directorio para imágenes temporales | ✅ |
| `TESSDATA_PREFIX` | `/usr/share/tesseract-ocr/5/tessdata` | Ruta a datos de Tesseract OCR | ✅ |

## 🔧 Variables Opcionales (Recomendadas)

Estas variables mejoran el funcionamiento pero tienen valores por defecto:

| Variable | Valor por Defecto | Descripción | Cuándo Configurar |
|----------|-------------------|-------------|------------------|
| `HOST` | `0.0.0.0` | Host del servidor | Solo si necesitas cambiar |
| `MAX_FILE_SIZE` | `10485760` (10MB) | Tamaño máximo de archivo | Si necesitas archivos más grandes |
| `TESSERACT_LANG` | `spa` | Idioma para OCR | Si necesitas otros idiomas |
| `RED_DETECTION_THRESHOLD` | `100` | Sensibilidad detección rojo | Si la detección no funciona bien |
| `LOG_LEVEL` | `INFO` | Nivel de logging | Para debugging |
| `GUNICORN_WORKERS` | `2` | Número de workers | Según carga del servidor |
| `GUNICORN_THREADS` | `2` | Threads por worker | Según carga del servidor |
| `GUNICORN_TIMEOUT` | `120` | Timeout en segundos | Si procesamiento es muy lento |

## 📝 Configuración para EasyPanel

### Mínima Configuración (Recomendada)

En EasyPanel, configura estas variables en la sección "Environment Variables":

```env
FLASK_ENV=production
PORT=5000
UPLOAD_FOLDER=/data/uploads
TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
```

### Configuración Completa (Opcional)

Si quieres personalizar más:

```env
FLASK_ENV=production
PORT=5000
UPLOAD_FOLDER=/data/uploads
TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
HOST=0.0.0.0
MAX_FILE_SIZE=10485760
TESSERACT_LANG=spa
LOG_LEVEL=INFO
GUNICORN_WORKERS=2
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
```

## 🐳 Configuración para Docker Compose

En `docker-compose.yml`, las variables se configuran así:

```yaml
environment:
  - FLASK_APP=app.py
  - FLASK_ENV=production
  - PORT=5000
  - TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
  - UPLOAD_FOLDER=/data/uploads
  - HOST=0.0.0.0
```

O usando un archivo `.env`:

```yaml
env_file:
  - .env
```

## 🔍 Descripción Detallada

### FLASK_APP
- **Valor:** `app.py`
- **Descripción:** Archivo principal de la aplicación Flask
- **Requerida:** ✅ Sí
- **Cuándo cambiar:** Nunca, a menos que cambies el nombre del archivo

### FLASK_ENV
- **Valor:** `production` o `development`
- **Descripción:** Modo de ejecución de Flask
- **Requerida:** ✅ Sí
- **Recomendación:** Usar `production` en servidores

### PORT
- **Valor:** `5000` (o cualquier puerto disponible)
- **Descripción:** Puerto donde escucha el servidor
- **Requerida:** ✅ Sí
- **Nota:** Debe coincidir con el puerto configurado en EasyPanel

### UPLOAD_FOLDER
- **Valor:** `/data/uploads` (Docker) o `./uploads` (local)
- **Descripción:** Directorio donde se guardan temporalmente las imágenes
- **Requerida:** ✅ Sí
- **Nota:** Debe coincidir con el volumen montado en Docker

### TESSDATA_PREFIX
- **Valor:** `/usr/share/tesseract-ocr/5/tessdata`
- **Descripción:** Ruta a los archivos de idioma de Tesseract
- **Requerida:** ✅ Sí
- **Nota:** En Docker, esta ruta es estándar. En local, puede variar según el sistema.

### HOST
- **Valor:** `0.0.0.0` (acepta todas las conexiones)
- **Descripción:** Dirección IP donde escucha el servidor
- **Requerida:** ❌ No (tiene valor por defecto)
- **Cuándo cambiar:** Solo si necesitas restringir acceso

### MAX_FILE_SIZE
- **Valor:** `10485760` (10MB)
- **Descripción:** Tamaño máximo de archivo en bytes
- **Requerida:** ❌ No
- **Cuándo cambiar:** Si necesitas procesar imágenes más grandes

### TESSERACT_LANG
- **Valor:** `spa` (español)
- **Descripción:** Idioma para OCR
- **Requerida:** ❌ No
- **Opciones:** `spa`, `eng`, `spa+eng`, etc.
- **Cuándo cambiar:** Si necesitas reconocer otros idiomas

### RED_DETECTION_THRESHOLD
- **Valor:** `100`
- **Descripción:** Sensibilidad para detectar áreas rojas (0-255)
- **Requerida:** ❌ No
- **Cuándo cambiar:** 
  - Si no detecta áreas rojas: bajar el valor (ej: 50)
  - Si detecta demasiadas áreas: subir el valor (ej: 150)

### LOG_LEVEL
- **Valor:** `INFO`
- **Descripción:** Nivel de detalle de los logs
- **Requerida:** ❌ No
- **Opciones:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Cuándo cambiar:** Usar `DEBUG` para troubleshooting

### GUNICORN_WORKERS
- **Valor:** `2`
- **Descripción:** Número de procesos workers
- **Requerida:** ❌ No
- **Fórmula recomendada:** `(2 × CPU cores) + 1`
- **Cuándo cambiar:** Según la carga del servidor

### GUNICORN_THREADS
- **Valor:** `2`
- **Descripción:** Threads por worker
- **Requerida:** ❌ No
- **Cuándo cambiar:** Para aplicaciones I/O intensivas

### GUNICORN_TIMEOUT
- **Valor:** `120` (2 minutos)
- **Descripción:** Tiempo máximo para procesar una petición
- **Requerida:** ❌ No
- **Cuándo cambiar:** Si el procesamiento de imágenes es muy lento

## ✅ Verificación

Para verificar que las variables están configuradas correctamente:

```bash
# En el contenedor Docker
docker exec caudalia env | grep -E "FLASK|PORT|UPLOAD|TESS"

# O desde dentro del contenedor
docker exec -it caudalia bash
env | grep -E "FLASK|PORT|UPLOAD|TESS"
```

## 🔐 Seguridad

**IMPORTANTE:** No subas archivos `.env` con valores reales al repositorio. Usa siempre `.env.example` como plantilla.

## 📚 Referencias

- [Documentación Flask - Configuration](https://flask.palletsprojects.com/en/2.3.x/config/)
- [Documentación Gunicorn - Settings](https://docs.gunicorn.org/en/stable/settings.html)
- [Documentación Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

