#!/bin/bash
# Script para obtener credentials.json en una sola línea
# Necesario para configurar la variable de entorno en Render

echo "📋 GOOGLE_CREDENTIALS_JSON para Render.com"
echo "==========================================="
echo ""
echo "Copia el siguiente contenido completo y pégalo en Render como variable de entorno:"
echo ""
echo "Key: GOOGLE_CREDENTIALS_JSON"
echo "Value:"
echo ""
cat credentials.json | tr -d '\n'
echo ""
echo ""
echo "==========================================="
echo "✅ Copia TODO desde el primer { hasta el último }"
