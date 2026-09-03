#!/bin/bash
# ============================================================
# COME TO CODE - 2S Informatique Plus
# Script d'installation Linux/macOS (PostgreSQL automatise)
# ============================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  COME TO CODE - 2S Informatique Plus${NC}"
echo -e "${BLUE}  Script d'installation Linux/macOS (PostgreSQL)${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""

# ============================================================
# [1/8] Verification de Python
# ============================================================
echo -e "${YELLOW}[1/8]${NC} Verification de Python..."
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERREUR: Python 3 n'est pas installe.${NC}"
    echo "Ubuntu/Debian : sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
echo -e "  ${GREEN}OK${NC} $(python3 --version) detecte."
echo ""

# ============================================================
# [2/8] Verification de PostgreSQL (psql)
# ============================================================
echo -e "${YELLOW}[2/8]${NC} Verification de PostgreSQL..."
if ! command -v psql &>/dev/null; then
    echo -e "${RED}ERREUR: psql introuvable.${NC}"
    echo "Installez PostgreSQL :"
    echo "  Ubuntu/Debian : sudo apt install postgresql postgresql-contrib"
    echo "  macOS         : brew install postgresql"
    exit 1
fi
echo -e "  ${GREEN}OK${NC} PostgreSQL (psql) detecte."
echo ""

# ============================================================
# [3/8] Configuration .env
# ============================================================
echo -e "${YELLOW}[3/8]${NC} Configuration de la base de donnees..."

if [ ! -f ".env" ]; then
    echo ""
    echo "Aucun fichier .env trouve. Configurons la base de donnees."
    echo "(Appuyez sur Entree pour garder la valeur par defaut entre crochets)"
    echo ""

    read -p "Nom de la base de donnees [come_to_code_db]: " DB_NAME
    DB_NAME=${DB_NAME:-come_to_code_db}

    read -p "Utilisateur applicatif a creer [ctc_user]: " DB_USER
    DB_USER=${DB_USER:-ctc_user}

    read -s -p "Mot de passe pour cet utilisateur (obligatoire): " DB_PASSWORD
    echo ""
    if [ -z "$DB_PASSWORD" ]; then
        echo -e "${RED}ERREUR: Le mot de passe ne peut pas etre vide.${NC}"
        exit 1
    fi

    read -p "Hote PostgreSQL [localhost]: " DB_HOST
    DB_HOST=${DB_HOST:-localhost}

    read -p "Port PostgreSQL [5432]: " DB_PORT
    DB_PORT=${DB_PORT:-5432}

    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(40))")

    cat > .env << EOF
DJANGO_SECRET_KEY=${SECRET}
DJANGO_DEBUG=True

DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
EOF
    echo ""
    echo -e "  ${GREEN}OK${NC} Fichier .env cree avec succes."
else
    echo "  Fichier .env existant detecte, lecture des parametres..."
    set -a
    source .env
    set +a
    echo "  Base : ${DB_NAME} / Utilisateur : ${DB_USER} / Hote : ${DB_HOST}:${DB_PORT}"
fi
echo ""

# ============================================================
# [4/8] Creation automatique du role et de la base PostgreSQL
# ============================================================
echo -e "${YELLOW}[4/8]${NC} Creation de la base de donnees PostgreSQL..."
echo ""
echo "Methode de connexion administrateur PostgreSQL :"
echo "  1) sudo -u postgres (recommande sur Linux, sans mot de passe)"
echo "  2) psql -U postgres avec mot de passe (Linux distant / macOS)"
read -p "Choix [1]: " PG_METHOD
PG_METHOD=${PG_METHOD:-1}

SQLFILE=$(mktemp)
cat > "$SQLFILE" << SQLEOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE ROLE "${DB_USER}" WITH LOGIN PASSWORD '${DB_PASSWORD}';
   ELSE
      ALTER ROLE "${DB_USER}" WITH PASSWORD '${DB_PASSWORD}';
   END IF;
END
\$do\$;
ALTER ROLE "${DB_USER}" SET client_encoding TO 'utf8';
ALTER ROLE "${DB_USER}" SET default_transaction_isolation TO 'read committed';
ALTER ROLE "${DB_USER}" SET timezone TO 'Africa/Ouagadougou';
SQLEOF

run_as_admin() {
    if [ "$PG_METHOD" = "1" ]; then
        sudo -u postgres psql -h "$DB_HOST" -p "$DB_PORT" "$@"
    else
        read -s -p "Mot de passe admin postgres: " PGADMIN_PASS
        echo ""
        PGPASSWORD="$PGADMIN_PASS" psql -U postgres -h "$DB_HOST" -p "$DB_PORT" "$@"
        unset PGADMIN_PASS
    fi
}

if ! run_as_admin -v ON_ERROR_STOP=1 -f "$SQLFILE" > /dev/null; then
    echo -e "${RED}ERREUR: Impossible de creer l'utilisateur PostgreSQL.${NC}"
    rm -f "$SQLFILE"
    exit 1
fi
rm -f "$SQLFILE"
echo -e "  ${GREEN}OK${NC} Utilisateur \"${DB_USER}\" pret."

DB_EXISTS=$(run_as_admin -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'")
if [ "$DB_EXISTS" != "1" ]; then
    echo "  Creation de la base \"${DB_NAME}\"..."
    run_as_admin -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"${DB_NAME}\" OWNER \"${DB_USER}\";" > /dev/null
    echo -e "  ${GREEN}OK${NC} Base \"${DB_NAME}\" creee."
else
    echo "  La base \"${DB_NAME}\" existe deja, reutilisation."
    run_as_admin -c "GRANT ALL PRIVILEGES ON DATABASE \"${DB_NAME}\" TO \"${DB_USER}\";" > /dev/null 2>&1 || true
fi
echo ""

# ============================================================
# [5/8] Environnement virtuel
# ============================================================
echo -e "${YELLOW}[5/8]${NC} Creation de l'environnement virtuel..."
[ -d "venv" ] && rm -rf venv
python3 -m venv venv
echo -e "  ${GREEN}OK${NC} Environnement virtuel cree."
echo ""

# ============================================================
# [6/8] Dependances
# ============================================================
echo -e "${YELLOW}[6/8]${NC} Installation des dependances..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt
echo -e "  ${GREEN}OK${NC} Dependances installees."
echo ""

# ============================================================
# [7/8] Migrations
# ============================================================
echo -e "${YELLOW}[7/8]${NC} Creation des tables dans la base de donnees..."
python manage.py migrate
python manage.py collectstatic --noinput --clear > /dev/null 2>&1 || true
echo -e "  ${GREEN}OK${NC} Tables creees."
echo ""

# ============================================================
# [8/8] Superutilisateur
# ============================================================
echo -e "${YELLOW}[8/8]${NC} Creation du compte administrateur..."
python manage.py createsuperuser || true
echo ""

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  Installation terminee avec succes !${NC}"
echo -e "${BLUE}  Lancez : bash start.sh${NC}"
echo -e "${BLUE}=====================================================${NC}"
