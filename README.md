# COFINANCE CI — Microfinance & Assurance Mobile

Plateforme de gestion de microcrédits, assurances mobiles et support client en temps réel avec mesure de satisfaction NPS.

## Stack

| Technologie | Version | Rôle |
|---|---|---|
| Python | ≥ 3.12 | Langage |
| Django | 6.0.6 | Framework web principal |
| Django REST Framework | 3.17.1 | API REST |
| Django Channels | 4.3.2 | WebSocket (chat temps réel) |
| drf-spectacular | ≥ 0.28 | Documentation Swagger/Redoc |
| SimpleJWT | ≥ 5.5 | Authentification JWT |
| Base de données | SQLite3 / PostgreSQL | Stockage |
| Frontend | Templates Django + JS vanilla | Interface utilisateur |

## Fonctionnalités détaillées

### Crédits
- Demande de crédit avec montant, durée, motif et revenus mensuels
- Scoring automatique d'éligibilité (ratio revenu/montant, durée)
- Workflow de validation : SOUMISE → ANALYSE → APPROUVEE / REJETEE → DECAISSEE
- Décaissement avec montant approuvé et date de début de remboursement
- Génération automatique de l'échéancier (paiement par échéance)
- API REST complète (CRUD + changement de statut)

### Remboursements
- Paiement par échéance avec suivi des statuts (EN_ATTENTE, PAYEE, RETARD)
- Pénalités de retard : 1% du montant dû par jour de retard
- Rappels automatiques : J-3 avant échéance, J+1 après retard, J-15 avant clôture
- API REST complète (CRUD + consultation des échéanciers)

### Assurances
- Catalogue de produits : nom, description, prix, durée
- Souscription client avec dates de début et fin
- Statut ACTIVE / EXPIRED avec suivi automatique de l'expiration
- API REST (consultation produits, souscription, suivi)

### Chat en temps réel
- WebSocket bidirectionnel via Django Channels
- Indicateur de frappe ("L'agent écrit...")
- Présence en ligne (statut connecté/déconnecté)
- Assignation manuelle d'un agent à une conversation
- Fermeture de conversation
- Historique persistant en base de données
- Fallback HTTP (AJAX) si WebSocket indisponible

### Notifications
- Génération automatique pour : changement statut crédit, échéance imminente, retard de paiement, souscription assurance
- Marquage lu / non lu
- API REST (liste, détail, marquage lu)

### NPS (Net Promoter Score)
- Enquête de satisfaction après décaissement d'un crédit, souscription d'assurance ou fermeture de chat
- Score de 0 à 10 avec catégorisation : Promoteur (9-10), Passif (7-8), Détracteur (0-6)
- Dashboard admin avec jauge NPS visuelle, compteurs et dernières réponses
- API REST (soumission, historique, dashboard stats)

### Dashboard
- Vue admin : taux d'approbation, taux de recouvrement, score NPS, KPIs globaux
- Vue agent : crédits en cours, conversations assignées, clients suivis
- Vue client : ses crédits, ses remboursements, ses assurances, son historique

### Rôles et permissions
- **ADMIN** : accès à tout (admin Django, admin-panel, dashboard global, API)
- **AGENT** : gestion des crédits clients, assignation chat, dashboard agent
- **CLIENT** : ses propres crédits, remboursements, assurances, chat

## Installation

### Prérequis
- Python ≥ 3.12
- pip
- Git

### Étapes

```bash
# 1. Cloner le dépôt
git clone <repo-url>
cd cofinance_ci

# 2. Créer et activer l'environnement virtuel
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. (Optionnel) Charger les données de démonstration
python manage.py seed_db

# 6. Lancer le serveur de développement
python manage.py runserver
```

Le site est accessible sur `http://localhost:8000/`.

### Créer un superutilisateur (admin)

```bash
python manage.py createsuperuser
```

L'interface d'administration Django est sur `http://localhost:8000/admin/`.

## Variables d'environnement

Toutes les variables sont optionnelles en développement. Des valeurs par défaut sont fournies.

| Variable | Défaut | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | Clé aléatoire intégrée | Clé secrète Django (obligatoire en production) |
| `DJANGO_DEBUG` | `True` | Mode debug (mettre `False` en production) |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hôtes autorisés (séparés par des virgules) |
| `DATABASE_URL` | SQLite3 (`db.sqlite3`) | URL de connexion PostgreSQL |
| `CORS_ALLOWED_ORIGINS` | — | Origines CORS autorisées |

Exemple de fichier `.env` :

```env
DJANGO_SECRET_KEY=une-clé-secrète-longue-et-aléatoire
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,example.com
DATABASE_URL=postgres://user:pass@localhost:5432/cofinance
CORS_ALLOWED_ORIGINS=https://app.example.com
```

## API REST

Documentation interactive : [`/api/docs/`](http://localhost:8000/api/docs/) (Swagger) et [`/api/redoc/`](http://localhost:8000/api/redoc/) (Redoc).

Tous les endpoints (sauf login/register) nécessitent un token JWT dans l'en-tête :

```
Authorization: Bearer <votre-token>
```

### Authentification

| Méthode | Route | Description | Corps |
|---|---|---|---|
| POST | `/api/accounts/register/` | Créer un compte | `{ "username", "password", "password2", "role", "phone_number" }` |
| POST | `/api/accounts/login/` | Obtenir un JWT | `{ "username", "password" }` → `{ "access", "refresh" }` |
| POST | `/api/accounts/refresh/` | Rafraîchir le token | `{ "refresh" }` |
| GET | `/api/accounts/profile/` | Voir son profil | — |
| PUT | `/api/accounts/profile/` | Modifier son profil | `{ "first_name", "last_name", "email", "phone_number" }` |
| POST | `/api/accounts/change-password/` | Changer son mot de passe | `{ "old_password", "new_password", "new_password2" }` |
| GET | `/api/accounts/users/` | Lister les utilisateurs (admin) | — |
| GET | `/api/accounts/users/<id>/` | Détail d'un utilisateur (admin) | — |

### Crédits

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/credits/` | Créer une demande de crédit |
| GET | `/api/credits/list/` | Lister ses crédits (client) ou tous (admin/agent) |
| GET | `/api/credits/<id>/` | Détail d'un crédit |
| PUT/PATCH | `/api/credits/<id>/update/` | Modifier un crédit |
| DELETE | `/api/credits/<id>/delete/` | Supprimer un crédit |
| PATCH | `/api/credits/<id>/status/` | Changer le statut (admin/agent) |

Exemple de création de crédit :

```json
POST /api/credits/
{
    "amount": "500000",
    "duration": 6,
    "purpose": "Achat matériel",
    "monthly_income": "300000"
}
```

### Remboursements

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/remboursements/` | Enregistrer un paiement |
| GET | `/api/remboursements/list/` | Lister les remboursements |
| GET | `/api/remboursements/<id>/` | Détail d'un remboursement |
| GET | `/api/remboursements/schedules/` | Lister les échéanciers |
| GET | `/api/remboursements/schedules/<id>/` | Détail d'une échéance |

### Assurances

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/assurances/products/` | Catalogue des produits |
| POST | `/api/assurances/subscribe/` | Souscrire à une assurance |
| GET | `/api/assurances/` | Lister ses souscriptions |
| GET | `/api/assurances/<id>/` | Détail d'une souscription |

### Chat

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/chat/` | Créer une conversation |
| GET | `/api/chat/list/` | Lister les conversations |
| GET | `/api/chat/<id>/messages/` | Voir les messages d'une conversation |
| POST | `/api/chat/<id>/assign/` | Assigner un agent à la conversation |
| POST | `/api/chat/<id>/close/` | Fermer la conversation |

**WebSocket** : `ws://localhost:8000/ws/chat/<room_id>/`

Types de messages WebSocket :

```json
// Message texte
{ "type": "chat_message", "message": "Bonjour, j'ai besoin d'aide" }

// Indicateur de frappe
{ "type": "user_typing", "is_typing": true }

// Statut en ligne
{ "type": "user_status", "status": "online" }
```

### Notifications

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/notifications/` | Lister ses notifications |
| GET | `/api/notifications/<id>/` | Détail d'une notification |
| PATCH | `/api/notifications/<id>/read/` | Marquer comme lue |

### Dashboard

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/dashboard/` | Données du tableau de bord |

Retourne des KPIs selon le rôle :

- **Admin** : taux approbation, taux recouvrement, NPS, crédits par statut, clients actifs
- **Agent** : crédits en cours, conversations ouvertes, clients assignés

### NPS (Satisfaction)

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/surveys/` | Soumettre une réponse NPS |
| GET | `/api/surveys/list/` | Historique de ses réponses (client) ou toutes (admin) |
| GET | `/api/surveys/dashboard/` | Stats NPS (admin/agent) |

Exemple de soumission NPS :

```json
POST /api/surveys/
{
    "score": 9,
    "comment": "Très bon service !",
    "context_type": "CREDIT",
    "context_id": 12
}
```

## Structure du projet

```
cofinance_ci/
├── accounts/           # Authentification, profils, rôles (ADMIN/AGENT/CLIENT)
│   ├── models.py       # User avec rôle, phone, online status
│   ├── serializers.py  # Register, Profile, User serializers
│   ├── views.py        # Login, Register, Profile, ChangePassword, UserList
│   └── urls.py         # Routes /api/accounts/
│
├── assurances/         # Produits d'assurance et souscriptions
│   ├── models.py       # InsuranceProduct, InsuranceSubscription
│   ├── serializers.py
│   ├── views.py        # Product list, subscription CRUD
│   └── urls.py
│
├── config/             # Configuration Django
│   ├── settings.py     # INSTALLED_APPS, MIDDLEWARE, DRF, Channels, Spectacular
│   ├── urls.py         # Routes racine (site + API + Swagger)
│   ├── asgi.py         # ASGI pour Channels WebSocket
│   └── wsgi.py         # WSGI standard
│
├── core/               # Vues templates du site web
│   └── views.py        # Toutes les vues rendues par template (600+ lignes)
│
├── credits/            # Gestion des microcrédits
│   ├── models.py       # Credit avec statut, scoring, montant, durée
│   ├── serializers.py  # CreditSerializer, CreditStatusSerializer
│   ├── views.py        # CRUD + changement de statut
│   └── urls.py
│
├── dashboard/          # API tableau de bord
│   ├── serializers.py  # DashboardSerializer (KPIs calculés)
│   ├── views.py        # DashboardView (admin/agent/client)
│   └── urls.py
│
├── notifications/      # Système de notifications
│   ├── models.py       # Notification avec titre, message, lu/non lu
│   ├── serializers.py
│   ├── views.py        # Liste, détail, marquage lu
│   ├── urls.py
│   └── management/
│       └── commands/
│           ├── seed_db.py          # Données de démonstration
│           └── check_reminders.py  # Rappels automatiques (cron)
│
├── remboursements/     # Remboursements et échéanciers
│   ├── models.py       # Remboursement, RepaymentSchedule
│   ├── serializers.py  # Avec calcul pénalités, jours de retard
│   ├── views.py        # CRUD + échéanciers
│   └── urls.py
│
├── support_chat/       # Chat temps réel
│   ├── models.py       # Conversation, Message
│   ├── serializers.py
│   ├── views.py        # CRUD conversations, assignation, fermeture
│   ├── consumers.py    # ChatConsumer WebSocket (Async)
│   ├── routing.py      # Routage WebSocket /ws/chat/<id>/
│   └── urls.py
│
├── surveys/            # Enquêtes NPS
│   ├── models.py       # NPSSurvey (score 0-10, contexte, catégorisation)
│   ├── serializers.py
│   ├── views.py        # Create, List, Dashboard stats
│   ├── signals.py      # Déclenchement auto après crédit/assurance/chat
│   └── urls.py
│
├── static/             # Fichiers statiques
│   ├── css/style.css   # Design system, composants, responsive
│   └── js/
│       ├── app.js          # Global (notifications, navigation)
│       ├── chat.js         # WebSocket client, fallback HTTP
│       ├── calculator.js   # Calculatrice crédit
│       └── nps.js          # Modale NPS
│
├── templates/          # Templates Django
│   ├── base.html           # Layout principal + modale NPS
│   ├── auth/               # login, register, profile
│   ├── dashboard/          # dashboard, dashboard_admin, dashboard_agent
│   ├── credits/            # list, create, detail, update
│   ├── remboursements/     # list
│   ├── assurances/         # list, subscribe
│   ├── chat/               # conversations, room
│   ├── notifications/      # list
│   ├── components/         # navbar, sidebar, footer, alerts
│   └── admin_panel/        # users, credits
│
├── tests.py            # 27 tests (modèles, API, signaux NPS, auth)
├── requirements.txt    # Dépendances Python
├── pyproject.toml      # Configuration projet, pytest, ruff, coverage
├── .gitignore          # Fichiers ignorés par Git
└── manage.py           # Point d'entrée Django
```

## Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture de code
pytest --cov

# En mode verbeux
pytest -v

# Un test spécifique
pytest tests.py::TestNPSSurvey::test_nps_create_api -v
```

**27 tests** couvrent :
- Modèles : création, propriétés, méthodes métier
- API : endpoints crédits, auth JWT (token valide/invalide)
- NPS : catégories Promoteur/Passif/Détracteur, API create/list/dashboard
- Signaux : déclenchement automatique NPS après décaissement, souscription, fermeture chat

## Scripts utiles

```bash
# Données de démonstration (utilisateurs, crédits, remboursements, assurances)
python manage.py seed_db

# Vérification des rappels et notifications en retard
python manage.py check_reminders

# Console Django interactive
python manage.py shell

# Collecte des fichiers statiques
python manage.py collectstatic
```

## Auteur

COFINANCE CI — © 2026
