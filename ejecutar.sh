#!/bin/bash
# Script para ejecutar el extractor usando el entorno virtual

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/extractor_imagenes.py" "$@"

