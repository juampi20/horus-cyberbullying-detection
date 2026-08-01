#!/bin/sh
set -eu

echo "🔒 Instalando Horus Cyberbullying Detection..."
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

echo "✓ Docker verificado"
echo ""

mkdir -p models data
echo "✓ Directorios creados"
echo ""

echo "Construyendo servicios..."
docker-compose build

echo ""
echo "Iniciando servicios..."
docker-compose up -d

echo ""
echo "✓ Instalación completa!"
echo ""
echo "Servicios iniciados:"
echo "  • FastAPI: http://localhost:8000"
echo "  • Docs: http://localhost:8000/docs"
echo "  • Streamlit: http://localhost:8501"
echo ""
echo "Comandos útiles:"
echo "  • Ver logs: docker-compose logs -f"
echo "  • Detener: docker-compose down"
echo "  • Estado: docker-compose ps"
