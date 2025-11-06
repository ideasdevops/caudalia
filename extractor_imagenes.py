#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de Texto y Números de Imágenes
Este programa utiliza OCR para extraer texto y datos numéricos de imágenes.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

try:
    from PIL import Image
    import pytesseract
except ImportError as e:
    print(f"Error: Faltan dependencias. Instala con: pip install -r requirements.txt")
    print(f"Error específico: {e}")
    exit(1)


def preprocesar_imagen(ruta_imagen: str) -> Image.Image:
    """
    Preprocesa la imagen para mejorar la calidad del OCR.
    
    Args:
        ruta_imagen: Ruta a la imagen a procesar
        
    Returns:
        Imagen preprocesada
    """
    imagen = Image.open(ruta_imagen)
    
    # Convertir a escala de grises si es necesario
    if imagen.mode != 'L':
        imagen = imagen.convert('L')
    
    # Aumentar contraste y nitidez
    from PIL import ImageEnhance
    
    # Aumentar contraste
    enhancer = ImageEnhance.Contrast(imagen)
    imagen = enhancer.enhance(1.5)
    
    # Aumentar nitidez
    enhancer = ImageEnhance.Sharpness(imagen)
    imagen = enhancer.enhance(2.0)
    
    return imagen


def extraer_texto_completo(ruta_imagen: str, idioma: str = 'spa') -> str:
    """
    Extrae todo el texto de una imagen usando OCR.
    
    Args:
        ruta_imagen: Ruta a la imagen
        idioma: Código de idioma para OCR (spa=español, eng=inglés)
        
    Returns:
        Texto extraído de la imagen
    """
    try:
        imagen = preprocesar_imagen(ruta_imagen)
        
        # Configuración de OCR para mejor precisión
        config = '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚáéíóúÑñ.,;:()[]{}!?@#$%&*-+=/ '
        
        texto = pytesseract.image_to_string(imagen, lang=idioma, config=config)
        return texto.strip()
    except Exception as e:
        print(f"Error al extraer texto de {ruta_imagen}: {e}")
        return ""


def extraer_numeros(texto: str) -> List[Dict[str, any]]:
    """
    Extrae todos los números del texto, incluyendo decimales, porcentajes, etc.
    
    Args:
        texto: Texto del cual extraer números
        
    Returns:
        Lista de diccionarios con información de los números encontrados
    """
    numeros = []
    
    # Patrones para diferentes tipos de números
    patrones = {
        'decimal': r'\d+\.\d+',  # Números decimales (ej: 123.45)
        'entero': r'\b\d+\b',    # Números enteros
        'porcentaje': r'\d+\.?\d*\s*%',  # Porcentajes
        'moneda': r'[\$€£]\s*\d+\.?\d*',  # Valores monetarios
        'fecha': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # Fechas
        'telefono': r'[\d\s\-\(\)]{10,}',  # Números de teléfono
    }
    
    for tipo, patron in patrones.items():
        matches = re.finditer(patron, texto)
        for match in matches:
            numeros.append({
                'tipo': tipo,
                'valor': match.group(),
                'posicion': match.start(),
                'linea': texto[:match.start()].count('\n') + 1
            })
    
    # Eliminar duplicados manteniendo el orden
    numeros_unicos = []
    valores_vistos = set()
    for num in numeros:
        clave = (num['valor'], num['posicion'])
        if clave not in valores_vistos:
            valores_vistos.add(clave)
            numeros_unicos.append(num)
    
    return numeros_unicos


def extraer_texto_estructurado(texto: str) -> Dict[str, any]:
    """
    Extrae texto estructurado identificando posibles etiquetas, títulos, etc.
    
    Args:
        texto: Texto completo extraído
        
    Returns:
        Diccionario con texto estructurado
    """
    lineas = [linea.strip() for linea in texto.split('\n') if linea.strip()]
    
    # Identificar posibles títulos (líneas cortas en mayúsculas o con formato especial)
    titulos = []
    parrafos = []
    
    for linea in lineas:
        # Si la línea es corta y está en mayúsculas, probablemente es un título
        if len(linea) < 50 and linea.isupper():
            titulos.append(linea)
        # Si la línea contiene números y texto, podría ser un dato estructurado
        elif re.search(r'\d+', linea):
            parrafos.append(linea)
        else:
            parrafos.append(linea)
    
    return {
        'titulos': titulos,
        'parrafos': parrafos,
        'total_lineas': len(lineas)
    }


def procesar_imagen(ruta_imagen: str, idioma: str = 'spa', guardar_json: bool = True) -> Dict[str, any]:
    """
    Procesa una imagen y extrae todo el texto y números.
    
    Args:
        ruta_imagen: Ruta a la imagen
        idioma: Idioma para OCR
        guardar_json: Si True, guarda los resultados en un archivo JSON
        
    Returns:
        Diccionario con todos los datos extraídos
    """
    ruta = Path(ruta_imagen)
    if not ruta.exists():
        raise FileNotFoundError(f"La imagen {ruta_imagen} no existe")
    
    print(f"Procesando: {ruta.name}...")
    
    # Extraer texto completo
    texto_completo = extraer_texto_completo(ruta_imagen, idioma)
    
    # Extraer números
    numeros = extraer_numeros(texto_completo)
    
    # Extraer texto estructurado
    texto_estructurado = extraer_texto_estructurado(texto_completo)
    
    # Compilar resultados
    resultados = {
        'archivo': ruta.name,
        'ruta_completa': str(ruta.absolute()),
        'texto_completo': texto_completo,
        'numeros_encontrados': numeros,
        'resumen_numeros': {
            'total': len(numeros),
            'por_tipo': {}
        },
        'texto_estructurado': texto_estructurado
    }
    
    # Contar números por tipo
    for num in numeros:
        tipo = num['tipo']
        resultados['resumen_numeros']['por_tipo'][tipo] = \
            resultados['resumen_numeros']['por_tipo'].get(tipo, 0) + 1
    
    # Guardar en JSON si se solicita
    if guardar_json:
        json_path = ruta.parent / f"{ruta.stem}_extraccion.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print(f"Resultados guardados en: {json_path}")
    
    return resultados


def procesar_carpeta(carpeta: str, idioma: str = 'spa', extensiones: List[str] = None) -> List[Dict[str, any]]:
    """
    Procesa todas las imágenes en una carpeta.
    
    Args:
        carpeta: Ruta a la carpeta
        idioma: Idioma para OCR
        extensiones: Lista de extensiones de archivo a procesar
        
    Returns:
        Lista de resultados de todas las imágenes
    """
    if extensiones is None:
        extensiones = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    
    carpeta_path = Path(carpeta)
    if not carpeta_path.exists():
        raise FileNotFoundError(f"La carpeta {carpeta} no existe")
    
    imagenes = []
    for ext in extensiones:
        imagenes.extend(carpeta_path.glob(f'*{ext}'))
        imagenes.extend(carpeta_path.glob(f'*{ext.upper()}'))
    
    resultados = []
    for imagen in imagenes:
        try:
            resultado = procesar_imagen(str(imagen), idioma)
            resultados.append(resultado)
        except Exception as e:
            print(f"Error procesando {imagen.name}: {e}")
    
    return resultados


def imprimir_resultados(resultados: Dict[str, any]):
    """
    Imprime los resultados de forma legible.
    
    Args:
        resultados: Diccionario con los resultados
    """
    print("\n" + "="*70)
    print(f"RESULTADOS PARA: {resultados['archivo']}")
    print("="*70)
    
    print("\n--- TEXTO COMPLETO ---")
    print(resultados['texto_completo'])
    
    print(f"\n--- NÚMEROS ENCONTRADOS ({resultados['resumen_numeros']['total']}) ---")
    if resultados['numeros_encontrados']:
        for num in resultados['numeros_encontrados']:
            print(f"  [{num['tipo']}] {num['valor']} (línea {num['linea']})")
    else:
        print("  No se encontraron números")
    
    print("\n--- RESUMEN POR TIPO ---")
    for tipo, cantidad in resultados['resumen_numeros']['por_tipo'].items():
        print(f"  {tipo}: {cantidad}")
    
    if resultados['texto_estructurado']['titulos']:
        print("\n--- TÍTULOS IDENTIFICADOS ---")
        for titulo in resultados['texto_estructurado']['titulos']:
            print(f"  • {titulo}")
    
    print("\n" + "="*70 + "\n")


def main():
    """Función principal del programa."""
    parser = argparse.ArgumentParser(
        description='Extrae texto y números de imágenes usando OCR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python extractor_imagenes.py imagen.jpg
  python extractor_imagenes.py imagen.jpg --idioma eng
  python extractor_imagenes.py --carpeta ./imagenes
  python extractor_imagenes.py imagen.jpg --no-json
        """
    )
    
    parser.add_argument('archivo', nargs='?', help='Ruta a la imagen a procesar')
    parser.add_argument('--carpeta', '-c', help='Procesar todas las imágenes en una carpeta')
    parser.add_argument('--idioma', '-l', default='spa', 
                       help='Idioma para OCR (spa=español, eng=inglés, spa+eng=ambos). Default: spa')
    parser.add_argument('--no-json', action='store_true', 
                       help='No guardar resultados en archivo JSON')
    parser.add_argument('--imprimir', '-p', action='store_true', 
                       help='Imprimir resultados en consola')
    
    args = parser.parse_args()
    
    try:
        if args.carpeta:
            # Procesar carpeta completa
            resultados = procesar_carpeta(args.carpeta, args.idioma)
            print(f"\n✓ Procesadas {len(resultados)} imágenes")
            
            if args.imprimir:
                for resultado in resultados:
                    imprimir_resultados(resultado)
        
        elif args.archivo:
            # Procesar archivo individual
            resultado = procesar_imagen(
                args.archivo, 
                args.idioma, 
                guardar_json=not args.no_json
            )
            
            if args.imprimir:
                imprimir_resultados(resultado)
            else:
                print("\n✓ Procesamiento completado")
                print(f"  Texto extraído: {len(resultado['texto_completo'])} caracteres")
                print(f"  Números encontrados: {resultado['resumen_numeros']['total']}")
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\nProceso cancelado por el usuario")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

