# API Location Car — Cameroun

API REST FastAPI pour une plateforme de location de voitures opérant au Cameroun (Douala, Yaoundé, Bafoussam, Garoua, ...). Authentification JWT (RS256), contrôle d'accès par rôle, montants exprimés en FCFA (XAF).

## Stack

- **FastAPI** + **Uvicorn**
- **SQLAlchemy 2.0** + **PostgreSQL** (psycopg2)
- **Alembic** pour les migrations
- **JWT RS256** (python-jose) pour l'authentification
- **Argon2** (passlib) pour le hashage des mots de passe
- **pydantic-settings** pour la configuration (`.env`)

## Installation

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
```

Copier `.env` (déjà présent) et vérifier les variables :

| Variable | Description |
|---|---|
| `DATABASE_URL` | URL PostgreSQL, ex: `postgresql+psycopg2://user:pass@localhost:5432/location_car_db` |
| `PRIVATE_KEY` / `PUBLIC_KEY` | Paire de clés RSA pour signer les JWT (format PEM, **entre guillemets** dans le `.env` car multi-lignes) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` / `ACCESS_TOKEN_EXPIRE_DAY` | Durées de vie des tokens acces/refresh |
| `FRONTEND_URL` | URL du frontend (utilisée pour le lien de réinitialisation de mot de passe et CORS) |
| `SMTP_*` | Identifiants SMTP pour l'envoi d'emails (bienvenue, reset password) |

Pour générer une nouvelle paire de clés RSA si besoin :

```bash
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
```

## Base de données

```bash
venv/bin/python -m alembic upgrade head
```

## Lancer l'API

```bash
venv/bin/python run.py
# ou
venv/bin/python -m uvicorn app.main:app --reload
```

Documentation interactive : http://127.0.0.1:8000/docs (Swagger) ou http://127.0.0.1:8000/redoc.

## Jeu de données de démonstration (contexte camerounais)

Un script idempotent peuple la base avec des agences, véhicules et utilisateurs réalistes situés à Douala, Yaoundé, Bafoussam et Garoua :

```bash
venv/bin/python -m scripts.seed_data
```

Il peut être relancé sans risque de doublons. Mot de passe commun à tous les comptes créés : **`Cameroun@2024`**.

Comptes créés :

| Rôle | Email | Agence |
|---|---|---|
| administrateur | `admin@locationcar.cm` | — |
| agence | `serge.fotso@doualauto.cm` | Doual'Auto Location (Douala) |
| agence | `aicha.oumarou@237rentcar.cm` | 237 Rent Car (Yaoundé) |
| agence | `jp.mbarga@westdrive.cm` | West Drive Location (Bafoussam) |
| agence | `fatimatou.abdoulaye@grandnordauto.cm` | Grand Nord Auto (Garoua) |
| client | `marie.ateba@gmail.com`, `christian.njoya@gmail.com`, ... | — |

## Rôles et droits d'accès

Trois rôles : `client`, `agence`, `administrateur`.

- Le **tout premier compte inscrit** sur une instance devient automatiquement `administrateur` (bootstrap). Ensuite, l'auto-inscription publique ne permet de choisir qu'entre `client` et `agence` — jamais `administrateur`.
- Un utilisateur `agence` gère **une seule agence** (`Agence.responsable_id`), et ne peut créer/modifier/supprimer que les véhicules de cette agence.
- Un `client` ne voit et n'annule que ses propres réservations/paiements/avis.
- Un `administrateur` a accès à tout.

Toutes les routes protégées attendent un header `Authorization: Bearer <access_token>`.

## Sessions (pensé pour le mobile)

- `POST /auth/login` renvoie un `acces_token` (courte durée, `ACCESS_TOKEN_EXPIRE_MINUTES`) et un `refresh_token` (longue durée, `ACCESS_TOKEN_EXPIRE_DAY`, 30 jours par défaut) — à stocker respectivement en mémoire et dans le stockage sécurisé de l'appareil (`flutter_secure_storage`).
- Chaque refresh tokens est enregistré en base (table `refresh_token`) et **tourne à chaque utilisation** : `POST /auth/refresh` renvoie un nouveau couple access+refresh et révoque l'ancien refresh token. S'il est réutilisé (vol/replay), il est rejeté (401).
- `POST /auth/logout` révoque explicitement un refresh token (à appeler à la déconnexion de l'app).

## Aperçu des endpoints (préfixe `/api/v1`)

| Méthode | Route | Description | Accès |
|---|---|---|---|
| POST | `/auth/login` | Connexion | public |
| POST | `/auth/refresh` | Nouveau access+refresh token (rotation) | public (refresh token valide) |
| POST | `/auth/logout` | Révoquer un refresh token | public (refresh token valide) |
| POST | `/auth/forgot-password` / `/auth/reset-password` | Réinitialisation mot de passe | public |
| POST | `/users/` | Inscription | public |
| GET | `/users/` | Liste des utilisateurs | administrateur |
| GET/PUT/DELETE | `/users/{id}` | Profil | soi-même ou administrateur |
| POST/GET/PUT/DELETE | `/agences/` | Agences (GET accepte `lat`/`lon`/`radius_km` pour trier par proximité) | création: agence/admin, lecture: public, modif: responsable/admin |
| POST/GET/PUT/DELETE | `/vehicules/` | Véhicules | création/modif: agence propriétaire ou admin, lecture: public |
| POST | `/vehicules/{id}/photo` | Téléverser la photo d'un véhicule (jpeg/png/webp, 5 Mo max) | agence propriétaire ou admin |
| POST/GET/PATCH/DELETE | `/reservations/` | Réservations | création: client, lecture/statut selon rôle |
| POST/GET/PATCH | `/paiements/` | Paiements | client (création), agence/admin (validation) |
| POST/GET/DELETE | `/avis/` | Avis | création: client, lecture: public, suppression: auteur/admin |

## Photos de véhicules

Les images sont stockées sur disque local (`uploads/vehicules/`) et servies statiquement sous `/static/vehicules/...`. `Vehicule.image_url` contient le chemin relatif — le client (Flutter) doit le préfixer avec l'URL de base de l'API. Pour la production, remplacer ce stockage local par un bucket S3/Cloudinary (le point d'entrée est `app/utils/storage.py`).

## Recherche géographique

`GET /agences/?lat=<lat>&lon=<lon>&radius_km=<rayon>` renvoie les agences ayant des coordonnées, triées par distance croissante (calcul Haversine, sans dépendance PostGIS), avec un champ `distance_km` par agence. Sans `lat`/`lon`, le comportement reste une pagination classique (`distance_km` vaut alors `null`). Les véhicules d'une zone peuvent ensuite être récupérés via `GET /vehicules/?agence_id=<id>` pour chaque agence proche.

## Exemple de scénario (contexte camerounais)

```bash
B=http://127.0.0.1:8000/api/v1

# Connexion d'un client
TOKEN=$(curl -s -X POST $B/auth/login -H "Content-Type: application/json" \
  -d '{"email":"marie.ateba@gmail.com","mot_de_passe":"Cameroun@2024"}' | jq -r .acces_token)

# Rechercher les véhicules disponibles à Douala (agence 1)
curl -s "$B/vehicules/?agence_id=1&statut=disponible" | jq

# Réserver la Toyota Corolla (id 1) du 1er au 5 août
curl -s -X POST $B/reservations/ -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"vehicule_id":1,"date_debut":"2026-08-01","date_fin":"2026-08-05"}'
```

## Notes

- Tous les montants (`prix_journalier`, `montant_total`, `montant` du paiement) sont exprimés en **FCFA (XAF)**, sans champ devise dédié.
- La suppression d'un véhicule, d'un utilisateur ou d'une agence ayant un historique lié (réservations, avis, paiement) est **refusée (409)** plutôt que de casser silencieusement les données historiques.
- L'envoi d'email (bienvenue, reset password) échoue silencieusement (loggé, non bloquant) si les identifiants SMTP dans `.env` ne sont pas valides.
- `uploads/` (images) n'est pas versionné (`.gitignore`) — le dossier est recréé automatiquement au démarrage de l'app.
