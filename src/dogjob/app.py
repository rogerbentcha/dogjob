from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

import dogjob.infra.db
from dogjob.api import health, test_auth
from dogjob.infra.auth import verify_api_key
from dogjob.infra.config import get_settings


# Vérifier la connexion à la bd au démarrage de l'app
@asynccontextmanager
async def lifespan(_: FastAPI):
    dogjob.infra.db.check_connection()
    yield

def create_app() -> FastAPI:
    # Lecture de la configuration au démarrage : une variable manquante fait échouer tout de suite.
    _ = get_settings()

    app = FastAPI(title="Dogjob", lifespan=lifespan)
    app.include_router(health.router)

    # test de la vérification de la clé API
    app.include_router(test_auth.router, dependencies=[Depends(verify_api_key)])
    return app



app = create_app()
