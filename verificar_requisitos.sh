#!/bin/bash
# Script para verificar que todos los requisitos estén instalados

echo "Verificando requisitos del sistema..."
echo ""

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python encontrado: $PYTHON_VERSION"
else
    echo "✗ Python3 no encontrado. Instala con: sudo apt-get install python3 python3-venv"
    exit 1
fi

# Verificar Tesseract
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1)
    echo "✓ Tesseract OCR encontrado: $TESSERACT_VERSION"
    
    # Verificar idiomas instalados
    echo ""
    echo "Idiomas de Tesseract disponibles:"
    tesseract --list-langs 2>&1 | grep -v "Warning" | tail -n +2 | sed 's/^/  - /'
else
    echo "✗ Tesseract OCR no encontrado"
    echo ""
    echo "Instala Tesseract con:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install tesseract-ocr"
    echo "  sudo apt-get install tesseract-ocr-spa  # Para español"
    echo "  sudo apt-get install tesseract-ocr-eng  # Para inglés"
    exit 1
fi

# Verificar entorno virtual
if [ -d "venv" ]; then
    echo ""
    echo "✓ Entorno virtual encontrado"
    
    # Verificar dependencias
    if [ -f "venv/bin/pip" ]; then
        echo ""
        echo "Verificando dependencias de Python..."
        if ./venv/bin/pip list | grep -q "Pillow"; then
            echo "  ✓ Pillow instalado"
        else
            echo "  ✗ Pillow no instalado. Ejecuta: ./venv/bin/pip install -r requirements.txt"
        fi
        
        if ./venv/bin/pip list | grep -q "pytesseract"; then
            echo "  ✓ pytesseract instalado"
        else
            echo "  ✗ pytesseract no instalado. Ejecuta: ./venv/bin/pip install -r requirements.txt"
        fi
    fi
else
    echo ""
    echo "✗ Entorno virtual no encontrado"
    echo "  Crea el entorno virtual con: python3 -m venv venv"
    echo "  Luego instala dependencias: ./venv/bin/pip install -r requirements.txt"
fi

echo ""
echo "Verificación completada!"

