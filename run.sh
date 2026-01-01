#!/bin/bash

# Script de inicio rápido para ConSmart
# Ejecuta la aplicación con Flet 0.80

echo "🚀 Iniciando ConSmart..."
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "❌ Error: No se encuentra main.py"
    echo "   Asegúrate de estar en el directorio del proyecto"
    exit 1
fi

# Ejecutar con uv
if command -v uv &> /dev/null; then
    echo "✅ Usando uv para ejecutar..."
    uv run flet run main.py
else
    echo "⚠️  uv no encontrado, usando flet directamente..."
    flet run main.py
fi
