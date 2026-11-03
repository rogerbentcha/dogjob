from contextlib import asynccontextmanager

from fastapi import FastAPI

from dogjob.api import health
from dogjob.infra.config import get_settings

import dogjob.infra.db 


# Vérifier la connexion à la bd au démarrage de l'app
@asynccontextmanager
async def lifespan(app: FastAPI):
    dogjob.infra.db.check_connection()
    yield

def create_app() -> FastAPI:
    # Lecture de la configuration au démarrage : une variable manquante fait échouer tout de suite.
    get_settings()

    app = FastAPI(title="Dogjob", lifespan=lifespan)
    app.include_router(health.router)
    return app



app = create_app()
