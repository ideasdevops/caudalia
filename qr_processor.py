#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador de Códigos QR y Formularios de Google
Escanea QR codes y rellena automáticamente formularios de Google Forms
"""

import re
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

try:
    from PIL import Image
    import cv2
    import numpy as np
    from pyzbar import pyzbar
except ImportError as e:
    print(f"Error: Faltan dependencias. Instala con: pip install -r requirements.txt")
    print(f"Error específico: {e}")
    exit(1)


def escanear_qr_imagen(ruta_imagen: str) -> Optional[str]:
    """
    Escanea un código QR en una imagen y devuelve el contenido.
    
    Args:
        ruta_imagen: Ruta a la imagen con el QR code
        
    Returns:
        Contenido del QR code o None si no se encuentra
    """
    try:
        # Leer imagen con OpenCV
        img = cv2.imread(ruta_imagen)
        if img is None:
            # Intentar con PIL si OpenCV falla
            pil_img = Image.open(ruta_imagen)
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        # Convertir a escala de grises para mejor detección
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Escanear códigos QR
        qr_codes = pyzbar.decode(gray)
        
        if qr_codes:
            # Devolver el primer QR code encontrado
            return qr_codes[0].data.decode('utf-8')
        
        return None
    
    except Exception as e:
        print(f"Error al escanear QR: {e}")
        return None


def escanear_qr_desde_base64(imagen_base64: str) -> Optional[str]:
    """
    Escanea un código QR desde una imagen en base64.
    
    Args:
        imagen_base64: Imagen en formato base64 (con o sin prefijo data:image)
        
    Returns:
        Contenido del QR code o None si no se encuentra
    """
    try:
        import base64
        from io import BytesIO
        
        # Remover prefijo si existe
        if ',' in imagen_base64:
            imagen_base64 = imagen_base64.split(',')[1]
        
        # Decodificar base64
        imagen_bytes = base64.b64decode(imagen_base64)
        imagen = Image.open(BytesIO(imagen_bytes))
        
        # Convertir a OpenCV
        import numpy as np
        img = cv2.cvtColor(np.array(imagen), cv2.COLOR_RGB2BGR)
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Escanear códigos QR
        qr_codes = pyzbar.decode(gray)
        
        if qr_codes:
            return qr_codes[0].data.decode('utf-8')
        
        return None
    
    except Exception as e:
        print(f"Error al escanear QR desde base64: {e}")
        return None


def parsear_url_google_forms(url: str) -> Dict[str, any]:
    """
    Parsea una URL de Google Forms y extrae información relevante.
    
    Args:
        url: URL del formulario de Google
        
    Returns:
        Diccionario con información del formulario
    """
    try:
        parsed = urlparse(url)
        
        # Extraer ID del formulario
        form_id = None
        if 'forms' in parsed.path:
            # Formato: /forms/d/FORM_ID/viewform
            parts = parsed.path.split('/')
            if 'forms' in parts:
                idx = parts.index('forms')
                if idx + 1 < len(parts):
                    form_id = parts[idx + 1]
        
        # Extraer parámetros de la URL
        params = parse_qs(parsed.query)
        
        return {
            'url_completa': url,
            'form_id': form_id,
            'parametros': params,
            'dominio': parsed.netloc
        }
    
    except Exception as e:
        print(f"Error al parsear URL: {e}")
        return {'url_completa': url, 'error': str(e)}


def identificar_campo_formulario(form_info: Dict, valor_buscar: str) -> Optional[Dict]:
    """
    Intenta identificar el campo correcto en un formulario de Google.
    
    Args:
        form_info: Información del formulario
        valor_buscar: Valor que se quiere insertar (números del medidor)
        
    Returns:
        Información del campo identificado o None
    """
    # Estrategias para identificar el campo:
    # 1. Buscar campos con nombres relacionados a "medidor", "caudal", "lectura", "valor"
    # 2. Buscar campos numéricos
    # 3. Usar el primer campo de texto disponible
    
    # Por ahora, retornamos información básica
    # La identificación real se hará en el frontend con JavaScript
    return {
        'estrategia': 'auto_detection',
        'valor': valor_buscar,
        'form_id': form_info.get('form_id')
    }


def generar_url_formulario_relleno(form_url: str, campo_id: str, valor: str) -> str:
    """
    Genera una URL con el formulario pre-rellenado (si Google Forms lo permite).
    
    Nota: Google Forms no siempre permite pre-rellenar campos directamente.
    Esta función prepara la URL pero puede requerir JavaScript para rellenar.
    
    Args:
        form_url: URL del formulario
        campo_id: ID del campo a rellenar
        valor: Valor a insertar
        
    Returns:
        URL modificada (puede requerir JavaScript adicional)
    """
    parsed = urlparse(form_url)
    params = parse_qs(parsed.query)
    
    # Agregar parámetro de pre-relleno (si está soportado)
    params['entry.' + campo_id] = [valor]
    
    new_query = urlencode(params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    
    return urlunparse(new_parsed)


def procesar_qr_y_formulario(ruta_imagen_qr: str, valor_medidor: str) -> Dict[str, any]:
    """
    Procesa un QR code y prepara la información para rellenar el formulario.
    
    Args:
        ruta_imagen_qr: Ruta a la imagen con el QR code
        valor_medidor: Valor obtenido del medidor (números extraídos)
        
    Returns:
        Diccionario con información del formulario y datos para rellenar
    """
    # Escanear QR
    qr_content = escanear_qr_imagen(ruta_imagen_qr)
    
    if not qr_content:
        return {
            'error': 'No se pudo escanear el código QR',
            'exito': False
        }
    
    # Verificar si es una URL de Google Forms
    if 'docs.google.com/forms' not in qr_content and 'forms.gle' not in qr_content:
        return {
            'error': 'El QR code no apunta a un formulario de Google',
            'qr_content': qr_content,
            'exito': False
        }
    
    # Parsear URL del formulario
    form_info = parsear_url_google_forms(qr_content)
    
    # Identificar campo
    campo_info = identificar_campo_formulario(form_info, valor_medidor)
    
    return {
        'exito': True,
        'qr_content': qr_content,
        'form_info': form_info,
        'campo_info': campo_info,
        'valor_medidor': valor_medidor,
        'url_formulario': qr_content
    }

