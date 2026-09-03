@echo off
title Come To Code - Demarrage
color 0B

echo.
echo =====================================================
echo   COME TO CODE - 2S Informatique Plus
echo   Demarrage du serveur
echo =====================================================
echo.

if not exist venv (
    echo Environnement virtuel introuvable.
    echo Lancez d'abord install.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Demarrage du serveur Django...
echo.
echo   Local  :  http://127.0.0.1:8000
echo   Reseau :  http://VOTRE-IP:8000
echo.
echo Ctrl+C pour arreter.
echo.

python manage.py runserver 0.0.0.0:8000
pause
