#!/bin/bash
# COME TO CODE – Script de démarrage Linux/macOS

BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo ""
echo -e "${BLUE}Come To Code – Démarrage du serveur${NC}"
echo ""

if [ ! -d "venv" ]; then
    echo "Environnement virtuel introuvable. Lancez d'abord : bash install.sh"
    exit 1
fi

source venv/bin/activate

LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
echo -e "  Local  : ${GREEN}http://127.0.0.1:8000${NC}"
echo -e "  Réseau : ${GREEN}http://${LOCAL_IP}:8000${NC}"
echo ""

python manage.py runserver 0.0.0.0:8000
