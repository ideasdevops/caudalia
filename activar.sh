#!/bin/bash
# Script para activar el entorno virtual

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/venv/bin/activate"
echo "✓ Entorno virtual activado"
echo "  Para desactivar, ejecuta: deactivate"

