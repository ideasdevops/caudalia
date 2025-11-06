# 🐳 Guía Docker - Caudalia

Esta guía explica cómo construir y ejecutar Caudalia usando Docker.

## 📁 Archivos Docker Creados

### Archivos Principales
- **`Dockerfile`** - Imagen Docker optimizada para producción
- **`docker-compose.yml`** - Orquestación de servicios
- **`.dockerignore`** - Archivos excluidos del build
- **`easypanel.json`** - Configuración para EasyPanel
- **`DEPLOY.md`** - Guía completa de despliegue

## 🏗️ Arquitectura Docker

### Multi-stage Build
El Dockerfile utiliza un build multi-etapa para optimizar el tamaño:

1. **Etapa Builder**: Instala dependencias Python
2. **Etapa Runtime**: Imagen final con solo lo necesario

### Componentes Incluidos
- **Python 3.11-slim**: Base ligera
- **Tesseract OCR**: Con soporte para español e inglés
- **OpenCV**: Procesamiento de imágenes
- **Gunicorn**: Servidor WSGI para producción
- **Flask**: Framework web

## 🚀 Uso Local con Docker Compose

### Construir y ejecutar

```bash
# Construir la imagen
docker-compose build

# Iniciar el servicio
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener el servicio
docker-compose down
```

### Acceder a la aplicación

Una vez iniciado, accede a:
- **URL:** http://localhost:5000
- **Health Check:** http://localhost:5000/health

## 🔧 Construcción Manual

### Construir la imagen

```bash
docker build -t caudalia:latest .
```

### Ejecutar el contenedor

```bash
docker run -d \
  --name caudalia \
  -p 5000:5000 \
  -v caudalia_uploads:/data/uploads \
  -v caudalia_logs:/data/logs \
  -v caudalia_cache:/data/cache \
  caudalia:latest
```

## 📦 Volúmenes

Los siguientes volúmenes se crean automáticamente con docker-compose:

- **uploads_data**: `/data/uploads` - Imágenes temporales
- **logs_data**: `/data/logs` - Logs de la aplicación
- **cache_data**: `/data/cache` - Cache de procesamiento

## 🔍 Verificación

### Verificar que el contenedor está funcionando

```bash
# Ver estado
docker ps | grep caudalia

# Ver logs
docker logs caudalia -f

# Verificar health check
curl http://localhost:5000/health
```

### Verificar Tesseract

```bash
# Entrar al contenedor
docker exec -it caudalia bash

# Verificar Tesseract
tesseract --version
tesseract --list-langs
```

## 🛠️ Desarrollo

### Reconstruir después de cambios

```bash
# Reconstruir sin cache
docker-compose build --no-cache

# Reiniciar
docker-compose up -d
```

### Ejecutar comandos en el contenedor

```bash
# Entrar al contenedor
docker exec -it caudalia bash

# Ejecutar script de verificación
python extractor_rojo.py imagen.jpg --imprimir
```

## 📊 Monitoreo

### Ver uso de recursos

```bash
docker stats caudalia
```

### Ver logs en tiempo real

```bash
docker-compose logs -f caudalia
```

## 🔒 Seguridad

- ✅ Usuario no-root (`appuser`) dentro del contenedor
- ✅ Permisos restringidos en directorios
- ✅ Variables de entorno para configuración
- ✅ Health checks configurados

## 🚀 Despliegue en EasyPanel

Para desplegar en EasyPanel, sigue las instrucciones en `DEPLOY.md`.

### Pasos rápidos:

1. Sube el código a tu repositorio Git
2. En EasyPanel, crea una nueva aplicación
3. Selecciona "SSH Git" como tipo
4. Configura el repositorio y branch
5. Añade los volúmenes especificados en `easypanel.json`
6. EasyPanel construirá y desplegará automáticamente

## 📝 Notas Importantes

- El puerto por defecto es **5000**
- Los volúmenes se crean automáticamente con docker-compose
- El health check verifica `/health` cada 30 segundos
- Gunicorn usa 2 workers y 2 threads por defecto
- Los logs se muestran en stdout/stderr para facilitar el monitoreo

## 🐛 Solución de Problemas

### Error: Puerto ya en uso
```bash
# Cambiar el puerto en docker-compose.yml
ports:
  - "8080:5000"  # Usar puerto 8080 en lugar de 5000
```

### Error: Permisos en volúmenes
```bash
# Ajustar permisos
docker exec -it caudalia chown -R appuser:appuser /data
```

### Error: Tesseract no funciona
```bash
# Verificar instalación
docker exec caudalia tesseract --version
docker exec caudalia tesseract --list-langs
```

### Reconstruir desde cero
```bash
# Eliminar todo
docker-compose down -v
docker rmi caudalia_caudalia

# Reconstruir
docker-compose build --no-cache
docker-compose up -d
```

