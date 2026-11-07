from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session

from dogjob.infra.config import get_settings

# Noms de contraintes prévisibles : Alembic en a besoin pour les modifier
# ou les supprimer dans les migrations suivantes.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


env = get_settings()

# database engine
# Ferry fournit une URL "postgresql://" : on force le driver psycopg (v3).
_database_url = env.database_url.get_secret_value().replace(
    "postgresql://", "postgresql+psycopg://", 1
)
engine = create_engine(_database_url)


def get_session():
    with Session(engine) as session:
        yield session


def check_connection():
    with engine.connect() as conn:
        _ = conn.execute(text("SELECT 1"))
