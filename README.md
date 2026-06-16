# COFINANCE CI — Microfinance & Assurance Mobile

Plateforme de gestion de microcrédits, assurances mobiles, et support client en temps réel.

## Stack

| Technologie | Version |
| Python | ≥ 3.12 |
| Django | 6.0.6 |
| Django REST Framework | 3.17.1 |
| Django Channels | 4.3.2 |
| Base de données | SQLite3 / PostgreSQL |
| Frontend | Templates Django + JS vanilla |

## Fonctionnalités

- **Crédits** : demande, analyse, approbation/rejet, décaissement, échéancier automatique
- **Remboursements** : paiement par échéance, pénalités de retard (1%/jour), rappels J-3/J+1/J-15
- **Assurances** : catalogue produits, souscription client, suivi expiration
- **Chat temps réel** : WebSocket, typing indicator, présence en ligne, assignation agent
- **Notifications** : automatiques (crédit, remboursement, assurance), marquage lu
- **Dashboard** : KPIs admin (taux approbation/recouvrement), vue agent, vue client
- **Rôles** : ADMIN / AGENT / CLIENT avec permissions granulaires
- **API REST** : documentation Swagger/Redoc intégrée
- **JWT Authentication** : accès API sécurisé

## Installation

```bash
# Cloner
git clone <repo-url> && cd cofinance_ci

# Créer l'environnement virtuel
python -m venv .venv && .venv\Scripts\activate  # Windows
# ou : source .venv/bin/activate                  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Migrations
python manage.py migrate

# Données de démonstration
python manage.py seed_db

# Lancer le serveur
python manage.py runserver
```

## Environnement (optionnel)

Variables supportées :

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,example.com
DATABASE_URL=postgres://user:pass@localhost:5432/cofinance
CORS_ALLOWED_ORIGINS=https://app.example.com
```

## API

Documentation : `/api/docs/` (Swagger) et `/api/redoc/` (Redoc).

Endpoints principaux :

| Méthode | Route | Description |
| POST | `/api/accounts/login/` | Obtenir un JWT |
| POST | `/api/accounts/register/` | Créer un compte |
| GET/POST | `/api/credits/` | Lister / Créer un crédit |
| PATCH | `/api/credits/<id>/status/` | Changer le statut |
| GET/POST | `/api/remboursements/` | Remboursements |
| GET/POST | `/api/assurances/` | Souscriptions |
| GET/POST | `/api/chat/` | Conversations |
| GET | `/api/notifications/` | Notifications |
| GET | `/api/dashboard/` | Données dashboard |

## Tests

```bash
pytest
pytest --cov  # avec couverture
```

## Auteur

COFINANCE CI — © 2026
