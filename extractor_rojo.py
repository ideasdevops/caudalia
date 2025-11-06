#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de Texto en Áreas Rojas
Extrae solo el texto que está marcado/subrayado en rojo en imágenes de caudalímetros.
"""

import re
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import cv2

try:
    from PIL import Image, ImageEnhance
    import pytesseract
except ImportError as e:
    print(f"Error: Faltan dependencias. Instala con: pip install -r requirements.txt")
    print(f"Error específico: {e}")
    exit(1)


def detectar_areas_rojas(imagen_path: str, umbral_rojo: int = 100) -> List[Tuple[int, int, int, int]]:
    """
    Detecta áreas rojas (subrayados/marcas) en la imagen.
    
    Args:
        imagen_path: Ruta a la imagen
        umbral_rojo: Sensibilidad para detectar rojo (0-255)
        
    Returns:
        Lista de tuplas (x, y, ancho, alto) con las coordenadas de las áreas rojas
    """
    # Leer imagen con OpenCV
    img = cv2.imread(imagen_path)
    if img is None:
        # Intentar con PIL si OpenCV falla
        pil_img = Image.open(imagen_path)
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Convertir a HSV para mejor detección de color
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Definir rangos para rojo (en HSV, el rojo está en dos rangos)
    # Rango 1: rojos con matiz bajo (0-10)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    
    # Rango 2: rojos con matiz alto (170-180)
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    # Crear máscaras para ambos rangos
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    
    # Combinar máscaras
    mask = cv2.bitwise_or(mask1, mask2)
    
    # Aplicar operaciones morfológicas para limpiar la máscara
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Obtener rectángulos que encierran las áreas rojas
    areas_rojas = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Filtrar áreas muy pequeñas (ruido)
        if w > 20 and h > 5:  # Mínimo ancho y alto para subrayados
            areas_rojas.append((x, y, w, h))
    
    # Ordenar por posición Y (de arriba a abajo)
    areas_rojas.sort(key=lambda a: a[1])
    
    return areas_rojas


def expandir_area_roja(x: int, y: int, w: int, h: int, ancho_img: int, alto_img: int, 
                       expansion_x: int = 10, expansion_y: int = 5) -> Tuple[int, int, int, int]:
    """
    Expande el área roja para capturar el texto completo que está subrayado.
    
    Args:
        x, y, w, h: Coordenadas del área roja
        ancho_img, alto_img: Dimensiones de la imagen
        expansion_x: Píxeles a expandir horizontalmente
        expansion_y: Píxeles a expandir verticalmente hacia arriba
        
    Returns:
        Tupla con coordenadas expandidas
    """
    # Expandir hacia los lados
    x_nuevo = max(0, x - expansion_x)
    w_nuevo = min(ancho_img - x_nuevo, w + (expansion_x * 2))
    
    # Expandir hacia arriba (donde está el texto sobre el subrayado)
    y_nuevo = max(0, y - expansion_y * 3)  # Más expansión hacia arriba
    h_nuevo = min(alto_img - y_nuevo, h + expansion_y)
    
    return (x_nuevo, y_nuevo, w_nuevo, h_nuevo)


def extraer_texto_de_area(imagen: Image.Image, area: Tuple[int, int, int, int], 
                          idioma: str = 'spa') -> str:
    """
    Extrae texto de un área específica de la imagen.
    
    Args:
        imagen: Imagen PIL
        area: Tupla (x, y, w, h) con las coordenadas
        idioma: Idioma para OCR
        
    Returns:
        Texto extraído
    """
    x, y, w, h = area
    
    # Recortar el área
    area_recortada = imagen.crop((x, y, x + w, y + h))
    
    # Preprocesar el área recortada
    # Convertir a escala de grises
    if area_recortada.mode != 'L':
        area_recortada = area_recortada.convert('L')
    
    # Aumentar contraste
    enhancer = ImageEnhance.Contrast(area_recortada)
    area_recortada = enhancer.enhance(2.0)
    
    # Aumentar nitidez
    enhancer = ImageEnhance.Sharpness(area_recortada)
    area_recortada = enhancer.enhance(2.0)
    
    # OCR en el área
    config = '--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚáéíóúÑñ.,;:()[]{}!?@#$%&*-+=/ m³hΣ+−'
    texto = pytesseract.image_to_string(area_recortada, lang=idioma, config=config)
    
    return texto.strip()


def procesar_caudalimetro(ruta_imagen: str, idioma: str = 'spa', 
                          guardar_debug: bool = False) -> Dict[str, any]:
    """
    Procesa una imagen de caudalímetro y extrae solo el texto marcado en rojo.
    
    Args:
        ruta_imagen: Ruta a la imagen
        idioma: Idioma para OCR
        guardar_debug: Si True, guarda imágenes de debug con las áreas detectadas
        
    Returns:
        Diccionario con los datos extraídos
    """
    ruta = Path(ruta_imagen)
    if not ruta.exists():
        raise FileNotFoundError(f"La imagen {ruta_imagen} no existe")
    
    # Cargar imagen
    imagen = Image.open(ruta_imagen)
    ancho, alto = imagen.size
    
    # Detectar áreas rojas
    areas_rojas = detectar_areas_rojas(ruta_imagen)
    
    if not areas_rojas:
        return {
            'archivo': ruta.name,
            'texto_rojo': [],
            'texto_completo': '',
            'areas_detectadas': 0,
            'error': 'No se detectaron áreas rojas en la imagen'
        }
    
    # Expandir áreas y extraer texto
    textos_rojos = []
    imagen_debug = None
    
    if guardar_debug:
        # Crear imagen de debug con OpenCV
        img_debug = cv2.imread(ruta_imagen)
        if img_debug is None:
            pil_img = Image.open(ruta_imagen)
            img_debug = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    for i, area in enumerate(areas_rojas):
        # Expandir área para capturar texto completo
        area_expandida = expandir_area_roja(area[0], area[1], area[2], area[3], 
                                           ancho, alto)
        
        # Extraer texto
        texto = extraer_texto_de_area(imagen, area_expandida, idioma)
        
        if texto:
            textos_rojos.append({
                'area': i + 1,
                'texto': texto,
                'coordenadas_originales': area,
                'coordenadas_expandidas': area_expandida
            })
        
        # Dibujar en imagen de debug
        if guardar_debug:
            x, y, w, h = area_expandida
            cv2.rectangle(img_debug, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img_debug, f"Area {i+1}", (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Guardar imagen de debug si se solicita
    if guardar_debug and img_debug is not None:
        debug_path = ruta.parent / f"{ruta.stem}_debug.jpg"
        cv2.imwrite(str(debug_path), img_debug)
    
    # Combinar todos los textos
    texto_completo = ' '.join([t['texto'] for t in textos_rojos])
    
    # Extraer números del texto completo
    numeros = extraer_numeros(texto_completo)
    
    resultados = {
        'archivo': ruta.name,
        'texto_rojo': textos_rojos,
        'texto_completo': texto_completo,
        'areas_detectadas': len(areas_rojas),
        'numeros_encontrados': numeros,
        'resumen': {
            'total_areas': len(areas_rojas),
            'total_textos': len(textos_rojos),
            'total_numeros': len(numeros)
        }
    }
    
    return resultados


def extraer_numeros(texto: str) -> List[Dict[str, any]]:
    """
    Extrae números del texto, incluyendo unidades como m³/h, m³, etc.
    """
    numeros = []
    
    # Patrón para valores con unidades (ej: 00959g, +0.377 m³/h, +265.313 m³)
    patrones = [
        (r'[+\-]?\d+\.?\d*\s*m³/h?', 'caudal'),  # Caudal: m³/h
        (r'[+\-]?\d+\.?\d*\s*m³', 'volumen'),     # Volumen: m³
        (r'[+\-]?\d+\.?\d+', 'decimal'),          # Decimales
        (r'\d+[a-zA-Z]', 'numero_letra'),         # Número seguido de letra (ej: 00959g)
        (r'\d+', 'entero')                         # Enteros
    ]
    
    for patron, tipo in patrones:
        matches = re.finditer(patron, texto)
        for match in matches:
            valor = match.group().strip()
            numeros.append({
                'tipo': tipo,
                'valor': valor,
                'posicion': match.start()
            })
    
    # Eliminar duplicados
    valores_unicos = []
    vistos = set()
    for num in numeros:
        clave = (num['valor'], num['posicion'])
        if clave not in vistos:
            vistos.add(clave)
            valores_unicos.append(num)
    
    return valores_unicos


def main():
    """Función principal para uso desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extrae texto marcado en rojo de imágenes de caudalímetros'
    )
    parser.add_argument('archivo', help='Ruta a la imagen')
    parser.add_argument('--idioma', '-l', default='spa', help='Idioma para OCR')
    parser.add_argument('--debug', '-d', action='store_true', 
                       help='Guardar imagen de debug con áreas detectadas')
    parser.add_argument('--json', '-j', action='store_true', 
                       help='Guardar resultados en JSON')
    
    args = parser.parse_args()
    
    try:
        resultados = procesar_caudalimetro(args.archivo, args.idioma, args.debug)
        
        print("\n" + "="*70)
        print(f"RESULTADOS PARA: {resultados['archivo']}")
        print("="*70)
        print(f"\nÁreas rojas detectadas: {resultados['areas_detectadas']}")
        
        if resultados['texto_rojo']:
            print("\n--- TEXTO EN ÁREAS ROJAS ---")
            for area in resultados['texto_rojo']:
                print(f"  Área {area['area']}: {area['texto']}")
        
        if resultados['numeros_encontrados']:
            print("\n--- NÚMEROS Y VALORES ---")
            for num in resultados['numeros_encontrados']:
                print(f"  [{num['tipo']}] {num['valor']}")
        
        print(f"\n--- TEXTO COMPLETO ---")
        print(resultados['texto_completo'])
        
        if args.json:
            json_path = Path(args.archivo).parent / f"{Path(args.archivo).stem}_resultado.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Resultados guardados en: {json_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

