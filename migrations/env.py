from logging.config import fileConfig

from alembic import context

# Importer le domaine enregistre les tables dans Base.metadata (nécessaire à l'autogénération).
import dogjob.domain  # noqa: F401
from dogjob.infra.db import Base, engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Le modèle cible : Alembic compare ces tables à la base pour générer les migrations.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Mode hors ligne (`alembic upgrade head --sql`) : écrit le SQL au lieu de l'exécuter."""
    context.configure(
        url=engine.url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Mode normal : se connecte à la base (même URL et même driver que l'application)."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
