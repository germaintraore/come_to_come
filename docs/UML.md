# 📐 DOCUMENTATION UML – Come To Code

> **2S Informatique Plus** · Diagrammes UML complets

---

## 1. Diagramme de Cas d'Utilisation

```
┌─────────────────────────────────────────────────────────────┐
│                  Système Come To Code                       │
│                                                             │
│   ┌─────────────────┐      ┌─────────────────────────┐     │
│   │  Consulter      │      │    S'inscrire            │     │
│   │  l'accueil      │      │    (créer un compte)     │     │
│   └────────┬────────┘      └────────────┬────────────┘     │
│            │                            │                   │
│   ┌────────┴────────┐      ┌────────────┴────────────┐     │
│   │  Découvrir      │      │    Se connecter          │     │
│   │  l'importance   │      │    (WhatsApp + MDP)      │     │
│   │  du code        │      └────────────┬────────────┘     │
│   └─────────────────┘                   │                   │
│                             ┌───────────┴───────────┐      │
│                             │   Voir le tableau      │      │
│                             │   de bord              │      │
│                             └───────────┬───────────┘      │
│                                         │                   │
│                             ┌───────────┴───────────┐      │
│                             │   Se déconnecter       │      │
│                             └───────────────────────┘      │
│                                                             │
│   ┌─────────────────────────────────────────────────┐      │
│   │   <<include>> Authentification requise           │      │
│   │   pour : tableau de bord, déconnexion           │      │
│   └─────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘

   👤 Visiteur                    👤 Apprenant (connecté)
   ─────────                      ────────────────────────
   - Accueil                      - Tableau de bord
   - Inscription                  - Déconnexion
   - Connexion

   👑 Administrateur
   ─────────────────
   - Gérer les apprenants
   - Activer/désactiver comptes
   - Accès /admin/
```

---

## 2. Diagramme de Classes

```
┌───────────────────────────────────────────────────┐
│                   Apprenant                        │
│            (AbstractBaseUser + PermissionsMixin)   │
├───────────────────────────────────────────────────┤
│ - id              : Integer (PK, AUTO)             │
│ - nom             : CharField(100)                 │
│ - prenom          : CharField(100)                 │
│ - whatsapp        : CharField(20) [UNIQUE]         │
│ - password        : CharField(128) [hashé]         │
│ - date_inscription: DateTimeField [auto]           │
│ - is_active       : BooleanField [default=True]    │
│ - is_staff        : BooleanField [default=False]   │
│ - is_superuser    : BooleanField [default=False]   │
│ - last_login      : DateTimeField [null]           │
├───────────────────────────────────────────────────┤
│ + __str__()       : str                            │
│ + nom_complet     : str @property                  │
│ + set_password()  : void                           │
│ + check_password(): bool                           │
│ + has_perm()      : bool                           │
└───────────────────────────────────────────────────┘
             ▲
             │ gère
┌────────────┴──────────────┐
│      ApprenantManager     │
│       (BaseUserManager)   │
├───────────────────────────┤
│ + create_user()           │
│ + create_superuser()      │
└───────────────────────────┘

┌───────────────────────────┐     ┌─────────────────────────┐
│     InscriptionForm       │     │     ConnexionForm        │
│       (ModelForm)         │     │         (Form)           │
├───────────────────────────┤     ├─────────────────────────┤
│ - nom                     │     │ - whatsapp               │
│ - prenom                  │     │ - password               │
│ - whatsapp                │     ├─────────────────────────┤
│ - password1               │     │ + clean()                │
│ - password2               │     │ + get_user()             │
├───────────────────────────┤     └─────────────────────────┘
│ + clean_password2()       │
│ + clean_whatsapp()        │
│ + save()                  │
└───────────────────────────┘
```

---

## 3. Diagramme de Séquence – Inscription

```
Apprenant       Navigateur      Django View     Django Form     Base de Données
    │               │               │               │                │
    │── GET /inscription/ ─────────►│               │                │
    │               │               │               │                │
    │               │◄── Formulaire HTML vide ──────│                │
    │               │               │               │                │
    │  Remplit le formulaire         │               │                │
    │               │               │               │                │
    │── POST /inscription/ ─────────►│               │                │
    │  (nom, prénom, whatsapp, MDP) │               │                │
    │               │               │──── InscriptionForm(POST) ────►│
    │               │               │               │                │
    │               │               │◄── form.is_valid() ────────────│
    │               │               │    [valide : True/False]       │
    │               │               │               │                │
    │               │               │  Si valide :  │                │
    │               │               │──── form.save() ─────────────►│
    │               │               │               │── INSERT INTO apprenant
    │               │               │               │                │
    │               │               │──── login(request, apprenant)  │
    │               │               │               │                │
    │               │◄── Redirect vers /tableau-de-bord/ ────────────│
    │               │               │               │                │
    │  Si invalide : │               │               │                │
    │               │◄── Formulaire avec erreurs ───│                │
    │               │               │               │                │
```

---

## 4. Diagramme de Séquence – Connexion

```
Apprenant       Navigateur      Django View     authenticate()   Session
    │               │               │               │               │
    │── GET /connexion/ ───────────►│               │               │
    │               │◄── Formulaire HTML vide ──────│               │
    │               │               │               │               │
    │  Saisit WhatsApp + MDP        │               │               │
    │── POST /connexion/ ──────────►│               │               │
    │               │               │               │               │
    │               │               │── authenticate(whatsapp, MDP)►│
    │               │               │               │               │
    │               │               │               │── Requête BDD │
    │               │               │               │◄── Apprenant  │
    │               │               │               │               │
    │               │               │◄── apprenant ou None ─────────│
    │               │               │               │               │
    │               │               │  Si apprenant trouvé :        │
    │               │               │─────────────────── login() ──►│
    │               │               │                   Session créée│
    │               │               │                               │
    │               │◄── Redirect /tableau-de-bord/ + Cookie Session│
    │               │               │               │               │
    │  Si échec :   │               │               │               │
    │               │◄── Formulaire + erreur "Identifiants incorrects"
    │               │               │               │               │
```

---

## 5. Diagramme d'Activité – Flux général

```
                    ┌─────────────────┐
                    │   DÉBUT         │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Page d'accueil  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │                             │
    ┌─────────▼──────────┐       ┌──────────▼─────────┐
    │  Clic "S'inscrire"  │       │  Clic "Connexion"   │
    └─────────┬──────────┘       └──────────┬──────────┘
              │                             │
    ┌─────────▼──────────┐       ┌──────────▼─────────┐
    │  Saisie du          │       │  Saisie WhatsApp    │
    │  formulaire         │       │  + Mot de passe     │
    └─────────┬──────────┘       └──────────┬──────────┘
              │                             │
    ┌─────────▼──────────┐       ┌──────────▼─────────┐
    │ Validation du form  │       │  Vérification BDD   │
    └─────────┬──────────┘       └──────────┬──────────┘
              │                             │
         ┌────┴────┐                   ┌────┴────┐
         │ Valide? │                   │ Valide? │
         └────┬────┘                   └────┬────┘
        OUI   │  NON               OUI  │    │ NON
              │   │                     │    │
              │   └─► Afficher erreurs  │    └─► Afficher erreur
              │   ◄────────────────┘    │
              │                         │
    ┌─────────▼─────────────────────────▼──────────────┐
    │           Créer session + Connexion               │
    └─────────────────────┬────────────────────────────┘
                          │
               ┌──────────▼──────────┐
               │   Tableau de bord   │
               └──────────┬──────────┘
                          │
               ┌──────────▼──────────┐
               │   Déconnexion ?     │
               └──────────┬──────────┘
                     OUI  │
               ┌──────────▼──────────┐
               │  Supprimer session  │
               └──────────┬──────────┘
                          │
               ┌──────────▼──────────┐
               │  Redirect Accueil   │
               └──────────┬──────────┘
                          │
                    ┌─────▼──────┐
                    │    FIN     │
                    └────────────┘
```

---

*Documentation UML – Come To Code · 2S Informatique Plus · 2025*
