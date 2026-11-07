FROM python:3.14-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
COPY . /app

# Disable development dependencies
ENV UV_NO_DEV=1

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync --locked

# Au démarrage : appliquer les migrations, puis lancer l'API.
# Si une migration échoue, le conteneur s'arrête et l'API ne démarre pas sur un schéma incohérent.
# `exec` donne le PID 1 à l'API, qui reçoit alors directement les signaux d'arrêt de Ferry.
# Le cron de relances surcharge cette commande et ne lance donc pas de migration.
CMD ["sh", "-c", "uv run alembic upgrade head && exec uv run dogjob"]