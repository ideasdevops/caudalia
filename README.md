# Extractor de Texto y Números de Caudalímetros

Sistema especializado para extraer datos de medidores caudalímetros usando la cámara de dispositivos móviles. **Extrae solo el texto y números marcados en rojo** en las imágenes.

## Características

- 📱 **Interfaz web móvil** - Funciona directamente desde el navegador del móvil
- 🔴 **Detección de áreas rojas** - Identifica automáticamente texto subrayado/marcado en rojo
- 📸 **Captura con cámara** - Usa la cámara del dispositivo móvil o selecciona desde galería
- 🎯 **Especializado en caudalímetros** - Optimizado para medidores de flujo
- ⚡ **Procesamiento en tiempo real** - Resultados instantáneos
- 📊 **Extracción inteligente** - Detecta valores como m³/h, m³, números con letras (ej: 00959g)
- 🌐 **Servidor web** - Accesible desde cualquier dispositivo en la red local

## Requisitos Previos

### 1. Instalar Tesseract OCR

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-spa  # Para español
sudo apt-get install tesseract-ocr-eng  # Para inglés
```

**Windows:**
1. Descargar el instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar y agregar Tesseract al PATH del sistema

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # Para idiomas adicionales
```

### 2. Crear Entorno Virtual e Instalar Dependencias

**IMPORTANTE:** Este proyecto usa un entorno virtual para evitar conflictos con el sistema.

```bash
# Crear el entorno virtual (solo la primera vez)
python3 -m venv venv

# Instalar dependencias en el entorno virtual
./venv/bin/pip install -r requirements.txt
```

O instalar manualmente:
```bash
./venv/bin/pip install Pillow pytesseract
```

## Uso

### 🚀 Modo Móvil (Recomendado para Caudalímetros)

Este es el modo principal del sistema, diseñado para usar con la cámara del móvil:

```bash
# Iniciar el servidor web
./iniciar_servidor.sh
```

El servidor mostrará las URLs disponibles. Abre una de ellas en tu dispositivo móvil:

1. **Activa la cámara** desde la interfaz web
2. **Captura una foto** del caudalímetro
3. **Procesa la imagen** - El sistema detectará automáticamente las áreas rojas
4. **Ver los resultados** - Solo se mostrará el texto marcado en rojo

**Nota:** Asegúrate de que tu móvil y el servidor estén en la misma red WiFi.

### 📁 Modo Línea de Comandos (Para procesar archivos)

#### Opción 1: Usar el script ejecutar.sh

Este script usa automáticamente el entorno virtual:

```bash
# Procesar una imagen individual
./ejecutar.sh imagen.jpg

# Procesar con idioma específico
./ejecutar.sh imagen.jpg --idioma eng

# Procesar todas las imágenes de la carpeta actual
./ejecutar.sh --carpeta .

# Ver resultados en consola
./ejecutar.sh imagen.jpg --imprimir
```

#### Extraer solo texto en rojo (Caudalímetros)

```bash
# Procesar imagen detectando solo áreas rojas
./venv/bin/python extractor_rojo.py imagen.jpg --imprimir

# Con imagen de debug para ver áreas detectadas
./venv/bin/python extractor_rojo.py imagen.jpg --debug --json
```

### Opción 2: Activar el entorno virtual manualmente

```bash
# Activar el entorno virtual
source activar.sh
# O alternativamente:
source venv/bin/activate

# Ahora puedes usar python directamente
python extractor_imagenes.py imagen.jpg
python extractor_imagenes.py imagen.jpg --idioma eng
python extractor_imagenes.py --carpeta ./imagenes
python extractor_imagenes.py imagen.jpg --imprimir

# Cuando termines, desactiva el entorno
deactivate
```

### Opción 3: Usar el Python del entorno virtual directamente

```bash
./venv/bin/python extractor_imagenes.py imagen.jpg
./venv/bin/python extractor_imagenes.py imagen.jpg --idioma eng
./venv/bin/python extractor_imagenes.py --carpeta .
```

## Cómo Funciona la Detección de Rojo

El sistema utiliza procesamiento de imágenes para:

1. **Detectar áreas rojas** - Identifica subrayados y marcas rojas en la imagen
2. **Expandir áreas** - Captura el texto completo sobre las marcas rojas
3. **Extraer texto** - Aplica OCR solo en las áreas detectadas
4. **Filtrar resultados** - Devuelve únicamente el texto marcado en rojo

Esto asegura que solo se extraigan los datos relevantes del caudalímetro, ignorando el resto de la información.

## Formato de Salida

El programa genera un archivo JSON con la siguiente estructura:

### Modo Móvil (API)

```json
{
  "archivo": "caudalimetro.jpg",
  "texto_rojo": [
    {
      "area": 1,
      "texto": "+0.377 m³/h",
      "coordenadas_originales": [120, 150, 200, 5],
      "coordenadas_expandidas": [110, 135, 220, 20]
    },
    {
      "area": 2,
      "texto": "+265.313 m³",
      "coordenadas_originales": [120, 180, 250, 5],
      "coordenadas_expandidas": [110, 165, 270, 20]
    }
  ],
  "texto_completo": "+0.377 m³/h +265.313 m³",
  "areas_detectadas": 2,
  "numeros_encontrados": [
    {
      "tipo": "caudal",
      "valor": "+0.377 m³/h"
    },
    {
      "tipo": "volumen",
      "valor": "+265.313 m³"
    }
  ],
  "resumen": {
    "total_areas": 2,
    "total_textos": 2,
    "total_numeros": 2
  }
}
```

### Modo Línea de Comandos (Extractor General)

```json
{
  "archivo": "imagen.jpg",
  "ruta_completa": "/ruta/completa/imagen.jpg",
  "texto_completo": "Todo el texto extraído...",
  "numeros_encontrados": [
    {
      "tipo": "decimal",
      "valor": "123.45",
      "posicion": 120,
      "linea": 3
    }
  ],
  "resumen_numeros": {
    "total": 5,
    "por_tipo": {
      "decimal": 2,
      "entero": 3
    }
  }
}
```

## Tipos de Valores Detectados (Caudalímetros)

- **caudal**: Valores de flujo con unidad m³/h (ej: +0.377 m³/h)
- **volumen**: Valores de volumen con unidad m³ (ej: +265.313 m³)
- **numero_letra**: Números seguidos de letras (ej: 00959g)
- **decimal**: Números con punto decimal (ej: 123.45)
- **entero**: Números enteros (ej: 42)

## Solución de Problemas

### Error: "externally-managed-environment"

Si ves este error al instalar paquetes, significa que debes usar el entorno virtual. Ya está creado en este proyecto, solo necesitas usar:

```bash
./venv/bin/pip install -r requirements.txt
```

O usar el script `ejecutar.sh` que ya maneja esto automáticamente.

### Error: "tesseract is not installed"

Asegúrate de tener Tesseract OCR instalado en tu sistema. Ver sección "Requisitos Previos".

### Error: "Failed to load language"

Instala el paquete de idioma correspondiente:
- Español: `sudo apt-get install tesseract-ocr-spa`
- Inglés: `sudo apt-get install tesseract-ocr-eng`

### Baja calidad de extracción

El programa incluye preprocesamiento automático, pero si la calidad es baja:
- Asegúrate de que la imagen tenga buena resolución
- Verifica que el texto esté claro y legible
- Prueba con diferentes idiomas usando `--idioma`

## Ejemplos

### Ejemplo 1: Usar desde móvil (Recomendado)
```bash
# En el servidor
./iniciar_servidor.sh

# Luego abre http://IP_DEL_SERVIDOR:5000 en tu móvil
# Captura foto del caudalímetro y procesa
```

### Ejemplo 2: Procesar imagen de caudalímetro desde línea de comandos
```bash
./venv/bin/python extractor_rojo.py caudalimetro.jpg --imprimir --debug
```

### Ejemplo 3: Procesar con imagen de debug para verificar detección
```bash
./venv/bin/python extractor_rojo.py imagen.jpg --debug --json
# Esto creará imagen_debug.jpg mostrando las áreas detectadas
```

## Notas Importantes

### Para Caudalímetros:
- ✅ **Solo extrae texto marcado en rojo** - El resto de la información se ignora
- ✅ **Optimizado para medidores** - Funciona mejor con caudalímetros estándar
- ✅ **Mejor con buena iluminación** - Asegúrate de que las marcas rojas sean visibles
- ✅ **Cámara trasera recomendada** - Mejor calidad que la frontal

### Técnicas:
- El sistema detecta automáticamente las áreas rojas usando procesamiento de color
- Expande las áreas para capturar el texto completo sobre los subrayados
- Funciona mejor con imágenes de alta resolución
- Los resultados se muestran en tiempo real en la interfaz web

### Solución de Problemas:
- Si no detecta áreas rojas, verifica que las marcas sean claramente rojas
- Usa el modo `--debug` para ver qué áreas está detectando
- Asegúrate de tener buena iluminación al capturar

