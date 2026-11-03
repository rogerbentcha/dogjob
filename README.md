# Dogjob

Dogjob est la source unique de vérité de ma recherche d'emploi. Je capture une offre en quelques secondes, depuis un lien ou une phrase, et je retrouve l'état de chaque candidature en posant simplement la question à mon assistant IA. Je n'ai plus à me souvenir de qui relancer ni quand : le système me le rappelle. Mon énergie va aux candidatures, pas à leur administration.

Spécification : [SPEC.md](SPEC.md) · Décisions d'architecture : [docs/ADR.md](docs/ADR.md)

## Démarrage

Prérequis : [uv](https://docs.astral.sh/uv/) (installe Python 3.14 si besoin).

```bash
uv sync
cp .env.example .env   # puis remplir les valeurs
uv run fastapi dev     # http://127.0.0.1:8000/health et /docs
```

Toute la configuration passe par des variables d'environnement préfixées `DOGJOB_` (voir `.env.example`). Aucun secret n'est versionné.

## Qualité

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

## Structure

```
src/dogjob/
  api/        routes REST, dépendance d'authentification
  mcp/        outils MCP
  services/   entreprise, candidature, relance
  domain/     modèles, statuts, machine d'états
  infra/      repositories, ResendAdapter, config
  jobs/       send_reminders.py
tests/
```
