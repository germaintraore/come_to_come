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
