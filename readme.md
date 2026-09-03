ÉTAPE 1 — ANALYSE DE L'ARCHITECTURE DE MON PROJET DJANGO
🎯 Objectif
L'objectif de cette première étape est de cartographier l'intégralité de ton projet réel "Come To Code", de comprendre la fonction de chaque dossier et fichier, et de voir comment les différentes briques logicielles s'emboîtent pour former une application web complète connectée à PostgreSQL.

🧠 Concept à comprendre
Un projet Django fonctionne selon le patron d'architecture MTV (Model - Template - View) :

Le Projet racine (config) : C'est le cerveau de configuration (paramètres globaux, routes principales, sécurité).
L'Application (accounts) : C'est un module métier autonome qui gère une responsabilité précise (ici, la gestion des apprenants, authentification, dashboard et exports).
Le serveur et la base de données : Django sert les pages HTML (rendu côté serveur avec Bootstrap 5) et persiste les données dans PostgreSQL.
📁 Fichiers concernés (Cartographie réelle de ton projet)
Voici la structure exacte de ton projet 

come_to_code
 :

text
come_to_code/
│
├── manage.py                   # Point d'entrée en ligne de commande pour piloter Django
├── requirements.txt            # Liste des dépendances Python (Django, psycopg2-binary, openpyxl)
├── .env                        # Variables d'environnement secrètes (Base de données, SECRET_KEY, DEBUG)
├── .env.example                # Modèle de configuration d'environnement sans données sensibles
├── install.bat / install.sh    # Scripts d'installation automatique pour Windows et Linux/Mac
├── start.bat / start.sh        # Scripts de démarrage rapide du serveur local
│
├── config/                     # DOSSIER DE CONFIGURATION GLOBALE DU PROJET
│   ├── __init__.py             # Indique à Python que ce dossier est un package
│   ├── settings.py             # Paramètres centraux (BDD PostgreSQL, apps, middleware, auth)
│   ├── urls.py                 # Aiguillage principal des URLs du site
│   └── wsgi.py                 # Point d'entrée pour les serveurs web de production (WSGI)
│
├── accounts/                   # APPLICATION MÉTIER : Gestion des comptes et apprenants
│   ├── __init__.py             # Package Python
│   ├── admin.py                # Configuration du panneau d'administration officiel Django
│   ├── apps.py                 # Déclaration et configuration de l'application 'accounts'
│   ├── forms.py                # Formulaires Django (validation, nettoyage des saisies utilisateur)
│   ├── models.py               # Modèle de données métier (Apprenant) et gestionnaire (ApprenantManager)
│   ├── urls.py                 # Routes spécifiques à l'application accounts (connexion, admin-panel...)
│   ├── views.py                # Logique métier et contrôleurs (réception requête -> traitement -> rendu HTML)
│   ├── migrations/             # Historique des évolutions de la base de données
│   │   ├── 0001_initial.py
│   │   └── 0002_apprenant_...py
│   └── management/             # Commandes personnalisées manage.py
│       └── commands/
│           └── create_default_admin.py # Commande pour créer l'admin par défaut
│
├── templates/                  # DOSSIER DES PAGES HTML (Moteur de templates Django)
│   ├── base.html               # Squelette commun (Navbar, Footer, Bootstrap 5, alertes)
│   └── accounts/               # Pages HTML spécifiques à l'app accounts
│       ├── accueil.html        # Page de présentation de la plateforme
│       ├── inscription.html    # Page du formulaire d'inscription
│       ├── connexion.html      # Page d'authentification (WhatsApp + mot de passe)
│       ├── tableau_de_bord.html# Espace personnel de l'apprenant connecté
│       └── admin_dashboard.html# Panneau d'administration personnalisé avec filtres & stats
│
├── static/                     # FICHIERS STATIQUES SOURCES (CSS, JS, images)
│   ├── css/style.css           # Feuilles de style personnalisées
│   └── js/main.js              # Scripts interactifs frontend
│
└── staticfiles/                # Dossier collecté pour la production (via collectstatic)
🔗 Relations entre les fichiers
Voici comment les fichiers de ton projet interagissent entre eux :

text
[Utilisateur / Navigateur]
        │
        ▼ (Requête HTTP)
[manage.py] ──> [config/settings.py] (Charge la configuration, DB, Apps)
        │
        ▼
[config/urls.py] (Distribue les URLs vers l'app accounts)
        │
        ▼
[accounts/urls.py] (Associe l'URL à la vue correspondante)
        │
        ▼
[accounts/views.py] ◄───► [accounts/forms.py] (Valide les données saisies)
        │
        ├───► [accounts/models.py] ◄───► [PostgreSQL] (Lecture / Écriture SQL)
        │
        └───► [templates/accounts/*.html] ◄─── [templates/base.html] (Génération HTML)
                    │
                    ▼ (Réponse HTTP HTML/CSS/JS)
         [Utilisateur / Navigateur]
Table des rôles et dépendances des fichiers clés
Fichier	Rôle principal	Ce qu'il appelle / importe	Ce qui l'appelle


manage.py
Point d'entrée de commandes	

config/settings.py
, Django Core	Le développeur via le terminal (python manage.py ...)


config/settings.py
Configuration globale & BDD	.env, modules système Python	Django au démarrage de toute commande ou serveur


config/urls.py
Routeur racine	

accounts/urls.py
, admin.site.urls	Django lors de la réception d'une URL


accounts/models.py
Définition de la table apprenant	django.db.models, AbstractBaseUser	

views.py
, 

forms.py
, 

admin.py


accounts/forms.py
Validation des formulaires	

accounts/models.py


accounts/views.py


accounts/views.py
Traitement de la logique métier	

models.py
, 

forms.py
, templates	

accounts/urls.py


templates/base.html
Gabarit global	

static/css/style.css
, CDN Bootstrap	Inclus par tous les autres templates via {% extends 'base.html' %}
🔄 Flux des données
Prenons un exemple concret dans ton application : L'accès au tableau de bord (/tableau-de-bord/).

L'utilisateur clique sur "Mon espace" ou navigue vers http://127.0.0.1:8000/tableau-de-bord/.
Django consulte 

config/urls.py
, qui redirige vers 

accounts/urls.py
.


accounts/urls.py
 identifie le chemin et déclenche la vue views.tableau_de_bord.
Dans 

accounts/views.py
, le décorateur @login_required vérifie si l'utilisateur est connecté via la session.
Si oui, Django récupère l'instance du modèle 

Apprenant
 dans request.user.
La vue passe request.user au template 

templates/accounts/tableau_de_bord.html
.
Le template injecte les variables (nom, prénom, numéro WhatsApp, formation, session) dans le HTML et renvoie la page finale au navigateur.
💻 Code de mon projet (Analyse des fondations)
Regardons comment ton projet est raccordé dans 

config/settings.py
 :

python
# 1. Déclaration de ton application métier
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',  # <--- TON APPLICATION PRINCIPALE
]
# 2. Modèle utilisateur personnalisé (remplace le User standard de Django)
AUTH_USER_MODEL = 'accounts.Apprenant'
# 3. Base de données PostgreSQL configurée dynamiquement
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     get_env('DB_NAME', 'come_to_code_db'),
        'USER':     get_env('DB_USER', 'postgres'),
        'PASSWORD': get_env('DB_PASSWORD', 'postgres'),
        'HOST':     get_env('DB_HOST', 'localhost'),
        'PORT':     get_env('DB_PORT', '5432'),
    }
}
🔎 Explication
Ce qui existe réellement dans ton projet :

C'est une application monolithique Django pure (Server-Side Rendering).
Il n'y a pas de Django REST Framework (DRF) ni de React : toute l'interface est générée directement par Django avec des templates HTML et Bootstrap 5.
L'authentification est personnalisée : le système n'utilise pas un nom d'utilisateur classique ou un email, mais le numéro WhatsApp comme identifiant unique (USERNAME_FIELD = 'whatsapp').
L'application propose une interface d'administration personnalisée (

admin_dashboard.html
) en plus de l'interface native Django (/admin/).
Des exports en CSV et Excel (openpyxl) sont intégrés pour exporter la liste des inscrits.
Ce qu'on déduit du code :

Le projet a été pensé pour être facile à déployer localement et rapidement utilisable pour des formations au Burkina Faso (fuseau horaire 'Africa/Ouagadougou' configuré dans 

settings.py
).
🧠 Raisonnement du développeur
Pourquoi avoir créé un modèle utilisateur personnalisé (Apprenant) dès le départ ? En Afrique de l'Ouest, beaucoup de personnes utilisent activement WhatsApp plutôt que l'e-mail. Utiliser le numéro WhatsApp comme identifiant principal évite les frictions lors de l'inscription.
Pourquoi un dashboard d'administration dédié (/admin-panel/) en plus de /admin/ ? L'admin natif de Django est très puissant mais austère. Créer une vue dédiée avec des compteurs (inscrits, actifs, inactifs), des filtres dynamiques et des boutons d'export CSV/Excel offre une expérience utilisateur plus intuitive pour les gestionnaires de la formation.
⚠️ Points importants : Fichiers à modifier vs à préserver
🟢 Fichiers modifiables sans risque pour faire évoluer le projet :


accounts/views.py
 : Pour ajouter ou adapter la logique d'une page.


accounts/forms.py
 : Pour ajouter des champs de saisie ou des règles de validation.


accounts/urls.py
 : Pour créer de nouvelles adresses URL.


templates/
 et 

static/css/style.css
 : Pour modifier l'apparence et le design.
🟡 Fichiers demandant une précaution spécifique :


accounts/models.py
 : Toute modification ici nécessite impérativement de générer et d'appliquer une migration (makemigrations puis migrate) sous peine de faire planter la base de données.
🔴 Fichiers à NE PAS modifier directement (sauf besoin d'infrastructure) :


manage.py
 : Fichier standard fourni par Django.


accounts/migrations/*.py
 : Fichiers générés automatiquement par Django. Ne les modifie jamais manuellement à moins d'être un expert en résolution de conflits de migrations.
.env : Contient tes mots de passe et clés secrètes. Ne jamais versionner sur GitHub public.
🧪 Comment tester l'architecture
Pour vérifier que tout le câblage de ton projet est intègre sans lancer le serveur web :

powershell
python manage.py check
Cette commande inspecte tous les modèles, les paramètres 

settings.py
 et la configuration sans erreur de syntaxe.

🏋️ Exercice
Sans exécuter de commande pour l'instant, regarde l'arborescence et réponds à cette situation :

Tu souhaites créer une nouvelle page publique appelée "À propos" (/a-propos/) qui affiche l'histoire du centre 2S Informatique Plus.

Quels sont les 3 fichiers que tu devras créer ou modifier, et dans quel ordre ?

❓ Questions de compréhension
Réponds à ces 5 questions pour valider que tu as bien assimilé la structure de ton projet :

Quel est le rôle exact de 

config/urls.py
 par rapport à 

accounts/urls.py
 ?
Si un utilisateur remplit le formulaire d'inscription sur le site, quel fichier Python est chargé de vérifier que le mot de passe fait au moins 8 caractères et que le numéro WhatsApp n'est pas déjà pris ?
Dans quel fichier est configurée l'adresse de connexion à la base de données PostgreSQL ?
Pourquoi le modèle s'appelle-t-il Apprenant et non le modèle User standard de Django ?
Que se passe-t-il si tu modifies un champ dans 

accounts/models.py
 sans exécuter les commandes de migration ?
📌 Ce que je dois retenir
Mon projet est découpé en deux dossiers principaux : config (le chef d'orchestre global) et accounts (l'application qui contient toute la logique de mon site).
Django fonctionne en chaîne : URL ➔ View ➔ Form/Model (Base de données) ➔ Template (HTML).


models.py
 est le reflet direct de mes tables PostgreSQL ; chaque changement structurel exige une migration.
Mon projet n'utilise pas d'API REST ou de React, c'est du Django classique générant du HTML avec Bootstrap 5.
👉 Prends le temps de réfléchir et réponds aux 5 questions et à l'exercice ci-dessus. J'analyserai ensuite tes réponses avant de passer à l'Étape 2 !

3:16 PM
