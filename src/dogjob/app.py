from fastapi import FastAPI

from dogjob.api import health
from dogjob.infra.config import get_settings


def create_app() -> FastAPI:
    # Lecture de la configuration au démarrage : une variable manquante fait échouer tout de suite.
    get_settings()

    app = FastAPI(title="Dogjob")
    app.include_router(health.router)
    return app


app = create_app()
