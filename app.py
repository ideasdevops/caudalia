#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Flask para procesar imágenes de caudalímetros desde dispositivos móviles
"""

import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import base64
from io import BytesIO

from extractor_rojo import procesar_caudalimetro, procesar_area_especifica

app = Flask(__name__)
CORS(app)  # Permitir CORS para acceso desde móviles

# Configuración
# Usar /data/uploads en producción (Docker) o uploads local en desarrollo
UPLOAD_FOLDER = Path(os.getenv('UPLOAD_FOLDER', '/data/uploads'))
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Página principal con interfaz móvil."""
    html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Extractor Caudalímetros</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 24px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .camera-container {
            position: relative;
            margin-bottom: 20px;
        }
        
        #video {
            width: 100%;
            border-radius: 10px;
            background: #000;
            display: none;
        }
        
        #canvas {
            display: none;
        }
        
        .preview-image {
            width: 100%;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        
        .preview-wrapper {
            position: relative;
            display: none;
            margin-bottom: 20px;
        }
        
        #selectionCanvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 10px;
            cursor: crosshair;
            display: none;
        }
        
        .selection-info {
            background: rgba(102, 126, 234, 0.9);
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            display: none;
            font-size: 14px;
        }
        
        .button-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        button {
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            color: white;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #6c757d;
        }
        
        .btn-success {
            background: #28a745;
        }
        
        .btn-danger {
            background: #dc3545;
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .results {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        
        .results h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 20px;
        }
        
        .result-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .result-item strong {
            color: #667eea;
            display: block;
            margin-bottom: 5px;
        }
        
        .result-value {
            font-size: 18px;
            color: #333;
            font-weight: 600;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
            display: none;
        }
        
        .file-input-wrapper {
            position: relative;
            overflow: hidden;
            display: inline-block;
            width: 100%;
        }
        
        .file-input-wrapper input[type=file] {
            position: absolute;
            left: -9999px;
        }
        
        .file-input-label {
            display: block;
            padding: 15px 25px;
            background: #6c757d;
            color: white;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .file-input-label:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Extractor Caudalímetros</h1>
        <p class="subtitle">Captura y extrae datos de medidores</p>
        
        <div class="camera-container">
            <video id="video" autoplay playsinline></video>
            <canvas id="canvas"></canvas>
            <div class="preview-wrapper" id="previewWrapper">
                <img id="preview" class="preview-image" alt="Vista previa">
                <canvas id="selectionCanvas"></canvas>
            </div>
        </div>
        
        <div class="selection-info" id="selectionInfo">
            Selecciona un área arrastrando sobre la imagen
        </div>
        
        <div class="button-group">
            <button id="startCamera" class="btn-primary">📷 Activar Cámara</button>
            <button id="capture" class="btn-success" style="display: none;">📸 Capturar</button>
            <button id="retake" class="btn-secondary" style="display: none;">🔄 Volver a Capturar</button>
            <button id="selectArea" class="btn-primary" style="display: none;">🎯 Seleccionar Área</button>
            <button id="process" class="btn-primary" style="display: none;">⚙️ Procesar Imagen Completa</button>
            <button id="processArea" class="btn-success" style="display: none;">✅ Procesar Área Seleccionada</button>
            
            <div class="file-input-wrapper">
                <label for="fileInput" class="file-input-label">📁 Seleccionar desde Galería</label>
                <input type="file" id="fileInput" accept="image/*" capture="environment">
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Procesando imagen...</p>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="results" id="results">
            <h2>📋 Resultados</h2>
            <div id="resultsContent"></div>
        </div>
    </div>
    
    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const preview = document.getElementById('preview');
        const previewWrapper = document.getElementById('previewWrapper');
        const selectionCanvas = document.getElementById('selectionCanvas');
        const selectionInfo = document.getElementById('selectionInfo');
        const startBtn = document.getElementById('startCamera');
        const captureBtn = document.getElementById('capture');
        const retakeBtn = document.getElementById('retake');
        const selectAreaBtn = document.getElementById('selectArea');
        const processBtn = document.getElementById('process');
        const processAreaBtn = document.getElementById('processArea');
        const fileInput = document.getElementById('fileInput');
        const loading = document.getElementById('loading');
        const error = document.getElementById('error');
        const results = document.getElementById('results');
        const resultsContent = document.getElementById('resultsContent');
        
        let stream = null;
        let currentImageData = null;
        let isSelecting = false;
        let selectionStart = { x: 0, y: 0 };
        let selectionEnd = { x: 0, y: 0 };
        let selectedArea = null;
        
        // Activar cámara
        startBtn.addEventListener('click', async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { 
                        facingMode: 'environment', // Cámara trasera
                        width: { ideal: 1920 },
                        height: { ideal: 1080 }
                    }
                });
                video.srcObject = stream;
                video.style.display = 'block';
                startBtn.style.display = 'none';
                captureBtn.style.display = 'block';
                hideError();
            } catch (err) {
                showError('Error al acceder a la cámara: ' + err.message);
            }
        });
        
        // Capturar foto
        captureBtn.addEventListener('click', () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            canvas.toBlob((blob) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    currentImageData = e.target.result;
                    preview.src = currentImageData;
                    preview.onload = () => {
                        setupPreview();
                    };
                    previewWrapper.style.display = 'block';
                    video.style.display = 'none';
                    captureBtn.style.display = 'none';
                    retakeBtn.style.display = 'block';
                    processBtn.style.display = 'block';
                    selectAreaBtn.style.display = 'block';
                    
                    // Detener cámara
                    if (stream) {
                        stream.getTracks().forEach(track => track.stop());
                        stream = null;
                    }
                };
                reader.readAsDataURL(blob);
            }, 'image/jpeg', 0.9);
        });
        
        // Volver a capturar
        retakeBtn.addEventListener('click', () => {
            previewWrapper.style.display = 'none';
            selectionCanvas.style.display = 'none';
            selectionInfo.style.display = 'none';
            currentImageData = null;
            selectedArea = null;
            retakeBtn.style.display = 'none';
            processBtn.style.display = 'none';
            selectAreaBtn.style.display = 'none';
            processAreaBtn.style.display = 'none';
            results.style.display = 'none';
            startBtn.style.display = 'block';
            hideError();
        });
        
        // Configurar preview y canvas de selección
        function setupPreview() {
            const rect = preview.getBoundingClientRect();
            selectionCanvas.width = preview.offsetWidth;
            selectionCanvas.height = preview.offsetHeight;
        }
        
        // Activar modo de selección
        selectAreaBtn.addEventListener('click', () => {
            isSelecting = true;
            selectedArea = null;
            selectionCanvas.style.display = 'block';
            selectionInfo.style.display = 'block';
            selectionCanvas.style.cursor = 'crosshair';
            processAreaBtn.style.display = 'none';
        });
        
        // Manejar selección de área
        function getEventPos(e) {
            const rect = selectionCanvas.getBoundingClientRect();
            const scaleX = preview.naturalWidth / preview.offsetWidth;
            const scaleY = preview.naturalHeight / preview.offsetHeight;
            return {
                x: (e.clientX - rect.left) * scaleX,
                y: (e.clientY - rect.top) * scaleY
            };
        }
        
        selectionCanvas.addEventListener('mousedown', (e) => {
            if (!isSelecting) return;
            const pos = getEventPos(e);
            selectionStart = pos;
            selectionEnd = pos;
        });
        
        selectionCanvas.addEventListener('mousemove', (e) => {
            if (!isSelecting) return;
            if (e.buttons === 1) {
                selectionEnd = getEventPos(e);
                drawSelection();
            }
        });
        
        selectionCanvas.addEventListener('mouseup', (e) => {
            if (!isSelecting) return;
            selectionEnd = getEventPos(e);
            drawSelection();
            finalizeSelection();
        });
        
        // Touch events para móviles
        selectionCanvas.addEventListener('touchstart', (e) => {
            if (!isSelecting) return;
            e.preventDefault();
            const touch = e.touches[0];
            const pos = getEventPos(touch);
            selectionStart = pos;
            selectionEnd = pos;
        });
        
        selectionCanvas.addEventListener('touchmove', (e) => {
            if (!isSelecting) return;
            e.preventDefault();
            const touch = e.touches[0];
            selectionEnd = getEventPos(touch);
            drawSelection();
        });
        
        selectionCanvas.addEventListener('touchend', (e) => {
            if (!isSelecting) return;
            e.preventDefault();
            finalizeSelection();
        });
        
        function drawSelection() {
            const ctx = selectionCanvas.getContext('2d');
            ctx.clearRect(0, 0, selectionCanvas.width, selectionCanvas.height);
            
            const x = Math.min(selectionStart.x / (preview.naturalWidth / preview.offsetWidth), 
                             selectionEnd.x / (preview.naturalWidth / preview.offsetWidth));
            const y = Math.min(selectionStart.y / (preview.naturalHeight / preview.offsetHeight),
                             selectionEnd.y / (preview.naturalHeight / preview.offsetHeight));
            const w = Math.abs(selectionEnd.x - selectionStart.x) / (preview.naturalWidth / preview.offsetWidth);
            const h = Math.abs(selectionEnd.y - selectionStart.y) / (preview.naturalHeight / preview.offsetHeight);
            
            // Dibujar rectángulo de selección
            ctx.strokeStyle = '#667eea';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.strokeRect(x, y, w, h);
            
            // Relleno semitransparente
            ctx.fillStyle = 'rgba(102, 126, 234, 0.2)';
            ctx.fillRect(x, y, w, h);
        }
        
        function finalizeSelection() {
            const x = Math.min(selectionStart.x, selectionEnd.x);
            const y = Math.min(selectionStart.y, selectionEnd.y);
            const ancho = Math.abs(selectionEnd.x - selectionStart.x);
            const alto = Math.abs(selectionEnd.y - selectionStart.y);
            
            if (ancho > 10 && alto > 10) {
                selectedArea = { x, y, ancho, alto };
                processAreaBtn.style.display = 'block';
                selectionInfo.textContent = `Área seleccionada: ${Math.round(ancho)}x${Math.round(alto)}px`;
            }
        }
        
        // Procesar área seleccionada
        processAreaBtn.addEventListener('click', async () => {
            if (!selectedArea || !currentImageData) return;
            
            loading.style.display = 'block';
            results.style.display = 'none';
            hideError();
            processAreaBtn.disabled = true;
            
            try {
                const blob = await (await fetch(currentImageData)).blob();
                const formData = new FormData();
                formData.append('image', blob, 'caudalimetro.jpg');
                formData.append('x', Math.round(selectedArea.x));
                formData.append('y', Math.round(selectedArea.y));
                formData.append('ancho', Math.round(selectedArea.ancho));
                formData.append('alto', Math.round(selectedArea.alto));
                
                const response = await fetch('/process-area', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    showError(data.error);
                } else {
                    displayAreaResults(data);
                }
            } catch (err) {
                showError('Error al procesar área: ' + err.message);
            } finally {
                loading.style.display = 'none';
                processAreaBtn.disabled = false;
            }
        });
        
        function displayAreaResults(data) {
            resultsContent.innerHTML = '';
            
            if (data.texto_una_linea || data.texto_extraido) {
                const texto = data.texto_una_linea || data.texto_extraido;
                const div = document.createElement('div');
                div.className = 'result-item';
                div.innerHTML = `
                    <strong>Texto Extraído (Izquierda a Derecha):</strong>
                    <div class="result-value" style="font-size: 20px; font-weight: bold; color: #667eea;">${texto}</div>
                `;
                resultsContent.appendChild(div);
            }
            
            if (data.numeros_encontrados && data.numeros_encontrados.length > 0) {
                const div = document.createElement('div');
                div.className = 'result-item';
                div.innerHTML = `
                    <strong>Números Detectados:</strong>
                    <div class="result-value">${data.numeros_encontrados.map(n => n.valor).join(', ')}</div>
                `;
                resultsContent.appendChild(div);
            }
            
            results.style.display = 'block';
        }
        
        // Procesar imagen
        processBtn.addEventListener('click', async () => {
            if (!currentImageData) return;
            
            loading.style.display = 'block';
            results.style.display = 'none';
            hideError();
            processBtn.disabled = true;
            
            try {
                // Convertir data URL a blob
                const blob = await (await fetch(currentImageData)).blob();
                const formData = new FormData();
                formData.append('image', blob, 'caudalimetro.jpg');
                
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    showError(data.error);
                } else {
                    displayResults(data);
                }
            } catch (err) {
                showError('Error al procesar: ' + err.message);
            } finally {
                loading.style.display = 'none';
                processBtn.disabled = false;
            }
        });
        
        function displayResults(data) {
            resultsContent.innerHTML = '';
            
            if (data.texto_rojo && data.texto_rojo.length > 0) {
                data.texto_rojo.forEach((area, index) => {
                    const div = document.createElement('div');
                    div.className = 'result-item';
                    div.innerHTML = `
                        <strong>Área ${area.area}:</strong>
                        <div class="result-value">${area.texto}</div>
                    `;
                    resultsContent.appendChild(div);
                });
            }
            
            if (data.numeros_encontrados && data.numeros_encontrados.length > 0) {
                const div = document.createElement('div');
                div.className = 'result-item';
                div.innerHTML = `
                    <strong>Valores Detectados:</strong>
                    <div class="result-value">${data.numeros_encontrados.map(n => n.valor).join(', ')}</div>
                `;
                resultsContent.appendChild(div);
            }
            
            if (data.texto_completo) {
                const div = document.createElement('div');
                div.className = 'result-item';
                div.innerHTML = `
                    <strong>Texto Completo:</strong>
                    <div>${data.texto_completo}</div>
                `;
                resultsContent.appendChild(div);
            }
            
            results.style.display = 'block';
        }
        
        function showError(message) {
            error.textContent = message;
            error.style.display = 'block';
        }
        
        function hideError() {
            error.style.display = 'none';
        }
    </script>
</body>
</html>
    """
    return render_template_string(html)


@app.route('/process', methods=['POST'])
def process_image():
    """Procesa una imagen subida y devuelve los resultados."""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Guardar archivo temporalmente
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        try:
            # Procesar imagen
            resultados = procesar_caudalimetro(
                str(filepath),
                idioma='spa',
                guardar_debug=False
            )
            
            # Limpiar archivo temporal
            filepath.unlink()
            
            return jsonify(resultados)
        
        except Exception as e:
            # Limpiar archivo en caso de error
            if filepath.exists():
                filepath.unlink()
            raise e
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process-area', methods=['POST'])
def process_area():
    """Procesa un área específica de una imagen subida."""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Obtener coordenadas del área
        data = request.form
        try:
            x = int(data.get('x', 0))
            y = int(data.get('y', 0))
            ancho = int(data.get('ancho', 0))
            alto = int(data.get('alto', 0))
        except (ValueError, TypeError):
            return jsonify({'error': 'Coordenadas del área inválidas'}), 400
        
        if ancho <= 0 or alto <= 0:
            return jsonify({'error': 'El área seleccionada debe tener dimensiones válidas'}), 400
        
        # Guardar archivo temporalmente
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        try:
            # Procesar área específica
            resultados = procesar_area_especifica(
                str(filepath),
                x=x,
                y=y,
                ancho=ancho,
                alto=alto,
                idioma='spa'
            )
            
            # Limpiar archivo temporal
            filepath.unlink()
            
            return jsonify(resultados)
        
        except Exception as e:
            # Limpiar archivo en caso de error
            if filepath.exists():
                filepath.unlink()
            raise e
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Endpoint de salud para verificar que el servidor está funcionando."""
    return jsonify({'status': 'ok', 'message': 'Servidor funcionando correctamente'})


if __name__ == '__main__':
    # Ejecutar en todas las interfaces para acceso desde móvil
    app.run(host='0.0.0.0', port=5000, debug=True)

