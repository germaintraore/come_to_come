# 📚 INSTALLATION & DÉPLOIEMENT – Come To Code

> **2S Informatique Plus** · Plateforme pédagogique d'initiation à la programmation

---

## Table des matières

1. [Structure du projet](#1-structure-du-projet)
2. [Installation rapide](#2-installation-rapide)
3. [Installation manuelle](#3-installation-manuelle)
4. [Déploiement réseau local](#4-déploiement-réseau-local)
5. [Version portable (clé USB)](#5-version-portable-clé-usb)
6. [Installateur Windows (.exe / Inno Setup)](#6-installateur-windows)
7. [Base de données](#7-base-de-données)
8. [Sauvegarde & Restauration](#8-sauvegarde--restauration)
9. [Administration](#9-administration)
10. [Dépannage](#10-dépannage)

---

## 1. Structure du projet

```
come_to_code/
├── config/                   # Configuration Django
│   ├── settings.py           # Paramètres
│   ├── urls.py               # Routes principales
│   └── wsgi.py               # Interface WSGI
├── accounts/                 # Application principale
│   ├── models.py             # Modèle Apprenant
│   ├── views.py              # Vues (accueil, auth, dashboard)
│   ├── forms.py              # Formulaires
│   ├── urls.py               # Routes de l'app
│   ├── admin.py              # Interface d'administration
│   └── migrations/           # Migrations BDD
├── templates/                # Templates HTML
│   ├── base.html             # Template de base
│   └── accounts/
│       ├── accueil.html
│       ├── inscription.html
│       ├── connexion.html
│       └── tableau_de_bord.html
├── static/                   # Fichiers statiques
│   ├── css/style.css
│   └── js/main.js
├── media/                    # Uploads utilisateurs
├── db.sqlite3                # Base de données SQLite
├── manage.py                 # CLI Django
├── requirements.txt          # Dépendances Python
├── install.bat               # Installation Windows
├── install.sh                # Installation Linux/macOS
├── start.bat                 # Démarrage Windows
└── start.sh                  # Démarrage Linux/macOS
```

---

## 2. Installation rapide

### Windows
```batch
# Double-cliquez sur install.bat
# ou dans le terminal :
install.bat
```

### Linux / macOS
```bash
chmod +x install.sh start.sh
bash install.sh
```

---

## 3. Installation manuelle

### Prérequis
- Python 3.10 ou supérieur
- pip (inclus avec Python)
- Git (optionnel)

### Étapes

```bash
# 1. Se placer dans le dossier du projet
cd come_to_code

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement
## Windows
venv\Scripts\activate
## Linux/macOS
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Créer les migrations
python manage.py makemigrations accounts
python manage.py migrate

# 6. Créer un superutilisateur (optionnel)
python manage.py createsuperuser

# 7. Lancer le serveur
python manage.py runserver 0.0.0.0:8000
```

---

## 4. Déploiement réseau local

### Objectif
Permettre à plusieurs ordinateurs d'accéder à l'application via le réseau WiFi ou câblé local.

### Configuration déjà intégrée
Le fichier `config/settings.py` contient :
```python
ALLOWED_HOSTS = ['*']  # Accepte toutes les connexions réseau
```

### Lancer le serveur en mode réseau

```bash
# Sur l'ordinateur SERVEUR :
python manage.py runserver 0.0.0.0:8000
```

### Trouver l'adresse IP du serveur

**Windows :**
```batch
ipconfig
# Cherchez "Adresse IPv4" ex : 192.168.1.5
```

**Linux :**
```bash
hostname -I
# ou
ip addr show
```

### Accès depuis les autres ordinateurs

Sur les ordinateurs **clients**, ouvrez un navigateur et tapez :
```
http://192.168.1.5:8000
```
(remplacez `192.168.1.5` par l'IP réelle du serveur)

### Schéma réseau

```
[PC Serveur]──────┐
  192.168.1.5     │
  :8000           │
                  ├── Switch/Routeur WiFi
[PC Client 1]─────┤
  http://192.168.1.5:8000
                  │
[PC Client 2]─────┘
  http://192.168.1.5:8000
```

### Pare-feu Windows
Si les autres PCs ne peuvent pas accéder, autorisez le port 8000 :
```batch
netsh advfirewall firewall add rule name="Django Come To Code" dir=in action=allow protocol=TCP localport=8000
```

---

## 5. Version portable (clé USB)

### Avantage
Copiez le dossier entier sur une clé USB et déplacez-le vers n'importe quel ordinateur.

### Sur le nouvel ordinateur

1. Copiez le dossier `come_to_code/` depuis la clé USB vers le bureau
2. Double-cliquez sur `install.bat` (Windows) ou `bash install.sh` (Linux)
3. Le script recrée automatiquement l'environnement et relance le serveur

### Remarque importante
- La base de données `db.sqlite3` est incluse dans le dossier
- Toutes les données (apprenants) sont transférées avec la clé USB
- Le dossier `venv/` peut être exclu de la clé USB (il sera recréé automatiquement)

---

## 6. Installateur Windows

### Option A – Inno Setup (recommandé)

#### Prérequis
- Téléchargez Inno Setup : https://jrsoftware.org/isdl.php

#### Script Inno Setup complet (`installer.iss`)

```pascal
[Setup]
AppName=Come To Code
AppVersion=1.0
AppPublisher=2S Informatique Plus
DefaultDirName={userappdata}\ComeToCode
DefaultGroupName=Come To Code
OutputDir=dist
OutputBaseFilename=ComeToCode_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Files]
; Inclure tous les fichiers du projet (hors venv et __pycache__)
Source: "come_to_code\*"; DestDir: "{app}"; \
  Flags: ignoreversion recursesubdirs createallsubdirs; \
  Excludes: "venv\*,__pycache__\*,*.pyc,staticfiles\*"

[Icons]
Name: "{group}\Démarrer Come To Code"; Filename: "{app}\start.bat"
Name: "{group}\Désinstaller Come To Code"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Come To Code"; Filename: "{app}\start.bat"; IconFilename: "{sys}\shell32.dll"

[Run]
Filename: "{app}\install.bat"; Description: "Configurer l'application"; \
  Flags: runhidden waituntilterminated; StatusMsg: "Installation en cours..."
Filename: "{app}\start.bat"; Description: "Lancer Come To Code maintenant"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\venv"
Type: filesandordirs; Name: "{app}\__pycache__"
```

#### Génération de l'installateur
1. Ouvrez Inno Setup Compiler
2. Chargez le fichier `installer.iss`
3. Cliquez **Build > Compile**
4. Le fichier `dist/ComeToCode_Setup.exe` est généré

---

### Option B – PyInstaller (fichier .exe)

```bash
pip install pyinstaller
pyinstaller --onefile --name ComeToCode manage.py
```

> ⚠️ Pour une application Django complète, Inno Setup est préférable car PyInstaller seul ne gère pas bien les assets statiques.

---

## 7. Base de données

> ⚠️ Depuis la version 2.0, ce projet utilise **PostgreSQL** au lieu de SQLite.

### ✅ Création automatique de la base (recommandé)

Depuis la version 2.1, **`install.bat` / `install.sh` créent automatiquement** :
- L'utilisateur applicatif PostgreSQL (`ctc_user` par défaut)
- La base de données (`come_to_code_db` par défaut)
- Le fichier `.env` avec tous les paramètres

**Tu n'as donc plus rien à créer manuellement dans PostgreSQL.** Il te suffit de :

1. **Installer PostgreSQL** (voir ci-dessous) — une seule fois
2. **Lancer `install.bat`** (ou `install.sh`)
3. Répondre aux quelques questions posées :
   - Nom de la base (Entrée = valeur par défaut)
   - Nom d'utilisateur applicatif (Entrée = valeur par défaut)
   - Mot de passe de cet utilisateur (à choisir, obligatoire)
   - **Mot de passe administrateur `postgres`** (celui défini lors de l'installation de PostgreSQL)

Le script se charge ensuite de tout : création du rôle, création de la base, droits, fichier `.env`, migrations Django, fichiers statiques, et compte administrateur.

> Sur Linux, le script propose aussi la méthode `sudo -u postgres` qui ne demande aucun mot de passe si tu es administrateur de la machine.

### Installer PostgreSQL (préalable obligatoire)

**Windows :**
1. Téléchargez l'installeur sur https://www.postgresql.org/download/windows/
2. Lancez l'installation (notez bien le mot de passe du compte `postgres` — il te sera redemandé par `install.bat`)
3. Cochez **"Add PostgreSQL to PATH"** durant l'installation (sinon `psql` ne sera pas trouvé)
4. PostgreSQL démarre automatiquement comme service Windows

**Linux (Ubuntu/Debian) :**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS :**
```bash
brew install postgresql
brew services start postgresql
```

### Méthode manuelle (optionnelle / dépannage)

Si tu préfères créer la base toi-même, ou si l'automatisation échoue, voici les commandes équivalentes :

```bash
# Connexion administrateur
sudo -u postgres psql          # Linux
psql -U postgres               # Windows ("SQL Shell (psql)")
```

```sql
CREATE DATABASE come_to_code_db;
CREATE USER ctc_user WITH PASSWORD 'votre_mot_de_passe_fort';
ALTER ROLE ctc_user SET client_encoding TO 'utf8';
ALTER ROLE ctc_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ctc_user SET timezone TO 'Africa/Ouagadougou';
GRANT ALL PRIVILEGES ON DATABASE come_to_code_db TO ctc_user;
\q
```

Puis crée toi-même le fichier `.env` (copie de `.env.example`) avec les mêmes valeurs, et lance :
```bash
python manage.py migrate
```

### MCD – Modèle Conceptuel de Données

```
┌─────────────────────────┐
│        APPRENANT        │
├─────────────────────────┤
│ PK  id                  │
│     nom                 │
│     prenom              │
│     whatsapp (unique)   │
│     password            │
│     date_inscription    │
│     is_active           │
│     is_staff            │
└─────────────────────────┘
```

### MLD – Modèle Logique de Données

```sql
APPRENANT (
  id                INTEGER      NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  nom               VARCHAR(100) NOT NULL,
  prenom            VARCHAR(100) NOT NULL,
  whatsapp          VARCHAR(20)  NOT NULL UNIQUE,
  password          VARCHAR(128) NOT NULL,  -- hashé avec PBKDF2
  date_inscription  TIMESTAMPTZ  NOT NULL DEFAULT now(),
  is_active         BOOLEAN      NOT NULL DEFAULT TRUE,
  is_staff          BOOLEAN      NOT NULL DEFAULT FALSE,
  is_superuser      BOOLEAN      NOT NULL DEFAULT FALSE,
  last_login        TIMESTAMPTZ  NULL
)
```

### MPD – Modèle Physique de Données (PostgreSQL)

```sql
CREATE TABLE apprenant (
    id                BIGSERIAL PRIMARY KEY,
    password          VARCHAR(128) NOT NULL,
    last_login        TIMESTAMPTZ,
    is_superuser      BOOLEAN NOT NULL DEFAULT FALSE,
    nom               VARCHAR(100) NOT NULL,
    prenom            VARCHAR(100) NOT NULL,
    whatsapp          VARCHAR(20) NOT NULL UNIQUE,
    date_inscription  TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff          BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_apprenant_whatsapp ON apprenant(whatsapp);
CREATE INDEX idx_apprenant_date_inscription ON apprenant(date_inscription DESC);
```

### Dictionnaire de données

| Champ             | Type PostgreSQL | Contrainte       | Description                          |
|-------------------|------------------|------------------|---------------------------------------|
| id                | BIGSERIAL        | PK, AUTO         | Identifiant unique                   |
| nom               | VARCHAR(100)     | NOT NULL         | Nom de famille de l'apprenant        |
| prenom            | VARCHAR(100)     | NOT NULL         | Prénom de l'apprenant                |
| whatsapp          | VARCHAR(20)      | NOT NULL, UNIQUE | Numéro WhatsApp (identifiant connexion)|
| password          | VARCHAR(128)     | NOT NULL         | Mot de passe hashé (PBKDF2+SHA256)   |
| date_inscription  | TIMESTAMPTZ      | DEFAULT now()    | Date et heure d'inscription          |
| is_active         | BOOLEAN          | DEFAULT TRUE     | Compte actif ou désactivé            |
| is_staff          | BOOLEAN          | DEFAULT FALSE    | Accès à l'interface d'administration |
| is_superuser      | BOOLEAN          | DEFAULT FALSE    | Tous les droits d'administration     |
| last_login        | TIMESTAMPTZ      | NULL             | Dernière connexion                   |

---

## 8. Sauvegarde & Restauration (PostgreSQL)

### Sauvegarder la base de données

```bash
# Sauvegarde complète au format SQL
pg_dump -U ctc_user -h localhost come_to_code_db > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Sauvegarde au format compressé (recommandé)
pg_dump -U ctc_user -h localhost -F c come_to_code_db > backups/backup_$(date +%Y%m%d).dump

# Alternative portable via Django (JSON, indépendant du SGBD)
python manage.py dumpdata accounts > backups/backup_$(date +%Y%m%d).json
```

**Windows (cmd) :**
```batch
pg_dump -U ctc_user -h localhost come_to_code_db > backups\backup.sql
python manage.py dumpdata accounts > backups\backup.json
```

### Restaurer la base de données

```bash
# Depuis un fichier SQL
psql -U ctc_user -h localhost come_to_code_db < backups/backup_20250101.sql

# Depuis un dump compressé
pg_restore -U ctc_user -h localhost -d come_to_code_db backups/backup_20250101.dump

# Depuis un JSON Django (après avoir recréé les tables vides)
python manage.py migrate
python manage.py loaddata backups/backup_20250101.json
```

### Automatiser les sauvegardes (cron Linux)

```bash
# Éditer le crontab
crontab -e

# Ajouter une sauvegarde quotidienne à 2h du matin
0 2 * * * pg_dump -U ctc_user -h localhost come_to_code_db > /chemin/vers/backups/backup_$(date +\%Y\%m\%d).sql
```

---

## 9. Administration

Come To Code propose **deux niveaux** d'administration : l'interface Django native et une interface personnalisée plus simple.

### A. Créer un compte administrateur

```bash
python manage.py createsuperuser
# Entrez un numéro WhatsApp et un mot de passe
```

Cette commande est aussi proposée automatiquement à la fin de `install.bat` / `install.sh`.

### B. Interface d'administration Django (technique)

Accédez à : `http://127.0.0.1:8000/admin/`

- Gestion complète et avancée des apprenants
- Filtres, recherche, modification en masse
- Réservée aux développeurs/techniciens

### C. Interface d'administration Come To Code (simplifiée)

Accédez à : `http://127.0.0.1:8000/admin-panel/`

Un lien **"Administration"** apparaît automatiquement dans le menu de navigation pour tout compte ayant le statut `is_staff = True`.

Cette interface permet de :
- **Voir tous les apprenants inscrits** dans un tableau clair avec avatar, statut, date
- **Voir des statistiques** : total, comptes actifs, comptes inactifs
- **Rechercher** un apprenant par nom, prénom ou numéro WhatsApp
- **Activer / désactiver** un compte en un clic
- **Supprimer** un compte (avec confirmation)
- **Télécharger la liste complète** au format :
  - **Excel (.xlsx)** — fichier mis en forme avec couleurs, prêt à imprimer ou archiver
  - **CSV** — pour import dans un tableur ou autre logiciel

> Pour donner les droits d'administration simplifiée à un apprenant existant sans lui donner accès à `/admin/` :
> ```bash
> python manage.py shell
> >>> from accounts.models import Apprenant
> >>> a = Apprenant.objects.get(whatsapp='+22670000000')
> >>> a.is_staff = True
> >>> a.save()
> ```

---

## 10. Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier que le port 8000 n'est pas déjà utilisé
## Windows
netstat -ano | findstr :8000
## Linux
lsof -i :8000

# Utiliser un autre port
python manage.py runserver 0.0.0.0:8080
```

### Les styles CSS ne s'affichent pas
```bash
python manage.py collectstatic --noinput
```

### Erreur "ModuleNotFoundError: No module named 'django'"
```bash
# Activez l'environnement virtuel d'abord
source venv/bin/activate   # Linux
venv\Scripts\activate      # Windows
```

### Un autre PC ne peut pas accéder au serveur
- Vérifiez que les deux PCs sont sur le même réseau
- Désactivez temporairement le pare-feu pour tester
- Vérifiez l'IP avec `ipconfig` (Windows) ou `hostname -I` (Linux)
- Assurez-vous que `ALLOWED_HOSTS = ['*']` est dans `settings.py`

### Erreur "psycopg2... could not connect to server"
- Vérifiez que PostgreSQL est démarré :
  - Windows : Services → "postgresql-x64-XX" → Démarrer
  - Linux : `sudo systemctl status postgresql` puis `sudo systemctl start postgresql`
- Vérifiez que `DB_HOST` et `DB_PORT` dans `.env` sont corrects (localhost / 5432 par défaut)

### Erreur "FATAL: password authentication failed for user"
- Le mot de passe dans `.env` (`DB_PASSWORD`) ne correspond pas à celui défini lors du `CREATE USER`
- Réinitialisez-le si besoin :
```sql
ALTER USER ctc_user WITH PASSWORD 'nouveau_mot_de_passe';
```
Puis mettez à jour `.env` avec la même valeur.

### Erreur "FATAL: database "come_to_code_db" does not exist"
- La base n'a pas été créée. Reconnectez-vous à `psql` et lancez :
```sql
CREATE DATABASE come_to_code_db OWNER ctc_user;
```

### Erreur "ModuleNotFoundError: No module named 'psycopg2'"
```bash
pip install psycopg2-binary --break-system-packages
# ou, dans l'environnement virtuel activé :
pip install -r requirements.txt
```

### Le bouton "Télécharger Excel" ne fonctionne pas
```bash
pip install openpyxl
```

---

*Documentation générée pour Come To Code – 2S Informatique Plus · 2025*
