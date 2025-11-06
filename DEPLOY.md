# 🚀 Guía de Deploy - Caudalia

Guía de despliegue del proyecto Caudalia (Extractor de Caudalímetros) en EasyPanel.

## 📋 Información del Proyecto

- **Nombre:** caudalia
- **Versión:** 1.0.0
- **Descripción:** Sistema de extracción de datos de caudalímetros usando OCR y detección de áreas rojas desde dispositivos móviles
- **Repositorio:** git@github.com:ideasdevops/caudalia.git (o el que corresponda)

## 🐳 Configuración Docker

### Dockerfile
- **Archivo:** `Dockerfile`
- **Base Image:** `python:3.11-slim`
- **Puerto:** `5000`
- **Servidor:** Gunicorn con Flask

## 📦 Volúmenes Requeridos

Configura los siguientes volúmenes en EasyPanel:

| Tipo | Nombre Local | Ruta en Contenedor | Descripción |
|------|--------------|-------------------|-------------|
| VOLUME | uploads | `/data/uploads` | Imágenes temporales subidas por usuarios |
| VOLUME | logs | `/data/logs` | Logs de la aplicación |
| VOLUME | cache | `/data/cache` | Cache de procesamiento |

## 🔧 Variables de Entorno

No se requieren variables de entorno obligatorias para el funcionamiento básico.

**Opcional:**
```env
FLASK_ENV=production
PORT=5000
UPLOAD_FOLDER=/data/uploads
TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
```

## 📝 Configuración en EasyPanel

### 1. Crear Aplicación

1. Ve a EasyPanel
2. Clic en "New App" o "+ Service"
3. Selecciona **"SSH Git"** como tipo de aplicación
4. Configura:
   - **Repositorio:** `git@github.com:ideasdevops/caudalia.git`
   - **Branch:** `main` (o la rama correspondiente)
   - **Dockerfile:** `Dockerfile`
   - **Puerto:** `5000`

### 2. Configurar Volúmenes

En la sección "Mounts", añade:

1. **VOLUME** - Nombre: `uploads`, Ruta: `/data/uploads`
2. **VOLUME** - Nombre: `logs`, Ruta: `/data/logs`
3. **VOLUME** - Nombre: `cache`, Ruta: `/data/cache`

### 3. Variables de Entorno (Opcional)

Si necesitas personalizar la configuración, añade las variables en la sección de variables de entorno.

### 4. Health Check

Configura el health check:
- **Path:** `/health`
- **Interval:** 30 segundos
- **Timeout:** 10 segundos
- **Retries:** 3

## 🏗️ Arquitectura

```
┌─────────────────────────────────────┐
│         EasyPanel / Docker          │
│                                     │
│  ┌──────────────────────────────┐ │
│  │      Gunicorn + Flask        │ │
│  │      Puerto: 5000            │ │
│  └──────────────────────────────┘ │
│                                     │
│  ┌──────────────────────────────┐ │
│  │     Volúmenes Persistentes    │ │
│  │  - /data/uploads (imágenes)    │ │
│  │  - /data/logs                 │ │
│  │  - /data/cache                │ │
│  └──────────────────────────────┘ │
│                                     │
│  Dependencias del Sistema:          │
│  - Tesseract OCR (spa, eng)         │
│  - OpenCV                          │
│  - Python 3.11                      │
└─────────────────────────────────────┘
```

## 🔄 Proceso de Deploy

1. **Build**: EasyPanel construye la imagen Docker usando el Dockerfile
2. **Dependencias**: Se instalan Tesseract OCR y dependencias Python
3. **Inicio**: Gunicorn inicia el servidor Flask en el puerto 5000
4. **Health Check**: EasyPanel verifica que el servicio esté funcionando

## 📱 Uso de la Aplicación

Una vez desplegado, accede a la aplicación desde:

- **URL:** `http://TU_SERVIDOR:5000`
- **Health Check:** `http://TU_SERVIDOR:5000/health`

### Desde Dispositivo Móvil:

1. Asegúrate de que el móvil esté en la misma red que el servidor
2. Abre el navegador y ve a la URL del servidor
3. Activa la cámara desde la interfaz web
4. Captura una foto del caudalímetro
5. Procesa la imagen
6. Verás solo el texto marcado en rojo

## 🛠️ Comandos Útiles

### Ver logs del contenedor
```bash
docker logs caudalia -f
```

### Ejecutar comando en el contenedor
```bash
docker exec -it caudalia bash
```

### Verificar Tesseract
```bash
docker exec caudalia tesseract --version
docker exec caudalia tesseract --list-langs
```

## 🔍 Solución de Problemas

### Error: Tesseract no encontrado
- Verifica que Tesseract esté instalado en la imagen
- Revisa los logs del build

### Error: No se detectan áreas rojas
- Verifica que la imagen tenga buena calidad
- Asegúrate de que las marcas rojas sean visibles
- Revisa los logs para ver errores de procesamiento

### Error: Puerto ya en uso
- Cambia el puerto en docker-compose.yml o en EasyPanel
- Verifica que no haya otro servicio usando el puerto 5000

## 📚 Recursos Adicionales

- [Documentación Flask](https://flask.palletsprojects.com/)
- [Documentación Gunicorn](https://gunicorn.org/)
- [Documentación Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Documentación OpenCV](https://opencv.org/)

