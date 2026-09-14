#!/usr/bin/env bash
# Arrêter le script si une commande échoue
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_default_admin
