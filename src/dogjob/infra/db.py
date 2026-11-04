from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session

from dogjob.infra.config import get_settings


class Base(DeclarativeBase):
    pass


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
