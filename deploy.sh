#!/bin/bash

# Script para actualizar y desplegar el juego

echo "🔵 Ingresá el mensaje del commit:"
read mensaje

# 1. Eliminar archivos viejos
echo "🗑️ Eliminando domino-web.zip..."
rm -f domino-web.zip

echo "🗑️ Eliminando carpeta build..."
rm -rf build

# 2. Git
echo "📦 Agregando cambios a git..."
git add .

echo "📝 Haciendo commit: $mensaje"
git commit -m "$mensaje"

echo "📤 Subiendo a GitHub..."
git push

# 3. Compilar con pygodide
echo "🔨 Compilando con pygodide..."
source venv/bin/activate
pygodide build .

# 4. Copiar HTML personalizado
echo "📄 Copiando index_web.html a build/index.html..."
cp index_web.html build/index.html

# 5. Crear ZIP
echo "📦 Creando domino-web.zip..."
zip -r domino-web.zip build/

echo "✅ ¡Listo! Subí domino-web.zip a itch.io"