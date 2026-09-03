@echo off
setlocal enabledelayedexpansion
title Come To Code - Installation
color 0B

echo.
echo =====================================================
echo   COME TO CODE - 2S Informatique Plus
echo   Script d'installation Windows (PostgreSQL)
echo =====================================================
echo.

REM ============================================================
REM [1/8] Verification de Python
REM ============================================================
echo [1/8] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou absent du PATH.
    echo Telechargez Python sur https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo Python detecte.
echo.

REM ============================================================
REM [2/8] Verification de PostgreSQL (psql)
REM ============================================================
echo [2/8] Verification de PostgreSQL...
where psql >nul 2>&1
if errorlevel 1 (
    echo ERREUR: La commande "psql" est introuvable dans le PATH.
    echo.
    echo Installez PostgreSQL : https://www.postgresql.org/download/windows/
    echo Lors de l'installation, cochez "Add PostgreSQL to PATH"
    echo ou ajoutez manuellement : C:\Program Files\PostgreSQL\XX\bin
    pause
    exit /b 1
)
echo PostgreSQL (psql) detecte.
echo.

REM ============================================================
REM [3/8] Configuration .env (creation ou lecture)
REM ============================================================
echo [3/8] Configuration de la base de donnees...

if not exist .env (
    echo.
    echo Aucun fichier .env trouve. Configurons la base de donnees.
    echo (Appuyez sur Entree pour garder la valeur par defaut entre crochets)
    echo.

    set "DB_NAME=come_to_code_db"
    set /p "DB_NAME=Nom de la base de donnees [come_to_code_db]: "
    if "!DB_NAME!"=="" set "DB_NAME=come_to_code_db"

    set "DB_USER=ctc_user"
    set /p "DB_USER=Utilisateur applicatif a creer [ctc_user]: "
    if "!DB_USER!"=="" set "DB_USER=ctc_user"

    set "DB_PASSWORD="
    set /p "DB_PASSWORD=Mot de passe pour cet utilisateur (obligatoire): "
    if "!DB_PASSWORD!"=="" (
        echo ERREUR: Le mot de passe ne peut pas etre vide.
        pause
        exit /b 1
    )

    set "DB_HOST=localhost"
    set /p "DB_HOST=Hote PostgreSQL [localhost]: "
    if "!DB_HOST!"=="" set "DB_HOST=localhost"

    set "DB_PORT=5432"
    set /p "DB_PORT=Port PostgreSQL [5432]: "
    if "!DB_PORT!"=="" set "DB_PORT=5432"

    REM Generer le fichier .env
    (
        echo DJANGO_SECRET_KEY=ctc-secret-%RANDOM%%RANDOM%%RANDOM%
        echo DJANGO_DEBUG=True
        echo.
        echo DB_NAME=!DB_NAME!
        echo DB_USER=!DB_USER!
        echo DB_PASSWORD=!DB_PASSWORD!
        echo DB_HOST=!DB_HOST!
        echo DB_PORT=!DB_PORT!
    ) > .env

    echo.
    echo Fichier .env cree avec succes.
) else (
    echo Fichier .env existant detecte, lecture des parametres...
    for /f "usebackq tokens=1,2 delims==" %%A in (".env") do (
        if "%%A"=="DB_NAME" set "DB_NAME=%%B"
        if "%%A"=="DB_USER" set "DB_USER=%%B"
        if "%%A"=="DB_PASSWORD" set "DB_PASSWORD=%%B"
        if "%%A"=="DB_HOST" set "DB_HOST=%%B"
        if "%%A"=="DB_PORT" set "DB_PORT=%%B"
    )
    echo Base : !DB_NAME! / Utilisateur : !DB_USER! / Hote : !DB_HOST!:!DB_PORT!
)
echo.

REM ============================================================
REM [4/8] Creation automatique du role et de la base PostgreSQL
REM ============================================================
echo [4/8] Creation de la base de donnees PostgreSQL...
echo.
echo Saisissez le mot de passe de l'administrateur PostgreSQL
echo (utilisateur "postgres", celui defini a l'installation de PostgreSQL).
echo.
set /p "PGADMIN_PASS=Mot de passe admin postgres: "

set "PGPASSWORD=!PGADMIN_PASS!"

REM Generer le script SQL de creation du role a partir du template
set "SQLFILE=%TEMP%\ctc_create_role.sql"
(
    echo DO
    echo $do$
    echo BEGIN
    echo    IF NOT EXISTS ^(SELECT FROM pg_catalog.pg_roles WHERE rolname = '!DB_USER!'^) THEN
    echo       CREATE ROLE "!DB_USER!" WITH LOGIN PASSWORD '!DB_PASSWORD!';
    echo    ELSE
    echo       ALTER ROLE "!DB_USER!" WITH PASSWORD '!DB_PASSWORD!';
    echo    END IF;
    echo END
    echo $do$;
    echo ALTER ROLE "!DB_USER!" SET client_encoding TO 'utf8';
    echo ALTER ROLE "!DB_USER!" SET default_transaction_isolation TO 'read committed';
    echo ALTER ROLE "!DB_USER!" SET timezone TO 'Africa/Ouagadougou';
) > "%SQLFILE%"

psql -U postgres -h !DB_HOST! -p !DB_PORT! -f "%SQLFILE%" -v ON_ERROR_STOP=1 >nul
if errorlevel 1 (
    echo.
    echo ERREUR: Impossible de creer l'utilisateur PostgreSQL.
    echo Verifiez le mot de passe admin et que PostgreSQL est demarre.
    set "PGPASSWORD="
    del "%SQLFILE%" >nul 2>&1
    pause
    exit /b 1
)
del "%SQLFILE%" >nul 2>&1
echo Utilisateur "!DB_USER!" pret.

REM Verifier si la base existe deja, sinon la creer
psql -U postgres -h !DB_HOST! -p !DB_PORT! -tc "SELECT 1 FROM pg_database WHERE datname = '!DB_NAME!'" > "%TEMP%\ctc_check.txt" 2>nul
findstr /C:"1" "%TEMP%\ctc_check.txt" >nul
if errorlevel 1 (
    echo Creation de la base "!DB_NAME!"...
    psql -U postgres -h !DB_HOST! -p !DB_PORT! -c "CREATE DATABASE \"!DB_NAME!\" OWNER \"!DB_USER!\";" -v ON_ERROR_STOP=1 >nul
    if errorlevel 1 (
        echo ERREUR: Impossible de creer la base de donnees.
        set "PGPASSWORD="
        del "%TEMP%\ctc_check.txt" >nul 2>&1
        pause
        exit /b 1
    )
    echo Base "!DB_NAME!" creee.
) else (
    echo La base "!DB_NAME!" existe deja, reutilisation.
    psql -U postgres -h !DB_HOST! -p !DB_PORT! -c "GRANT ALL PRIVILEGES ON DATABASE \"!DB_NAME!\" TO \"!DB_USER!\";" >nul 2>&1
)
del "%TEMP%\ctc_check.txt" >nul 2>&1
set "PGPASSWORD="
set "PGADMIN_PASS="
echo.

REM ============================================================
REM [5/8] Creation de l'environnement virtuel Python
REM ============================================================
echo [5/8] Creation de l'environnement virtuel...
if exist venv (
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ERREUR: Impossible de creer l'environnement virtuel.
    pause
    exit /b 1
)
echo Environnement virtuel cree.
echo.

REM ============================================================
REM [6/8] Installation des dependances
REM ============================================================
echo [6/8] Installation des dependances...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo ERREUR: Echec de l'installation des dependances.
    pause
    exit /b 1
)
echo Dependances installees.
echo.

REM ============================================================
REM [7/8] Migrations Django (creation des tables)
REM ============================================================
echo [7/8] Creation des tables dans la base de donnees...
python manage.py migrate
if errorlevel 1 (
    echo ERREUR: Echec des migrations Django.
    echo Verifiez les parametres dans le fichier .env
    pause
    exit /b 1
)
python manage.py collectstatic --noinput --clear >nul 2>&1
echo Tables creees avec succes.
echo.

REM ============================================================
REM [8/8] Compte administrateur
REM ============================================================
echo [8/8] Creation du compte administrateur...
echo Repondez aux questions (numero WhatsApp + mot de passe).
python manage.py createsuperuser
echo.

echo =====================================================
echo   Installation terminee avec succes !
echo   Lancez start.bat pour demarrer le serveur.
echo =====================================================
echo.
pause
