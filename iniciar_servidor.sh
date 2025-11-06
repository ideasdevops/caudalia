#!/bin/bash
# Script para iniciar el servidor Flask

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Iniciando servidor Flask..."
echo ""
echo "El servidor estará disponible en:"
echo "  - Local: http://localhost:5000"
echo "  - Red local: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Abre esta URL en tu dispositivo móvil para usar la cámara."
echo ""
echo "Presiona Ctrl+C para detener el servidor."
echo ""

"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/app.py"

