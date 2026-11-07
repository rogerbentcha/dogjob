from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dogjob.infra.db import Base


class Status(StrEnum):
    TO_APPLY = "to_apply"  # À postuler
    APPLIED = "applied"  # Postulé
    INTERVIEW = "interview"  # Entretien
    NO_RESPONSE = "no_response"  # Sans suite
    OFFER_RECEIVED = "offer_received"  # Offre reçue
    REJECTED = "rejected"  # Refusé


class Source(StrEnum):
    MANUAL = "manual"  # Manuel
    AUTO = "auto"  # Automatique : mis à jour par le cron


def _pg_enum(enum_cls: type[StrEnum], name: str) -> Enum:
    """Type ENUM Postgres qui stocke les valeurs ("to_apply") et non les noms ("TO_APPLY")."""
    return Enum(enum_cls, name=name, values_callable=lambda e: [m.value for m in e])


StatusType = _pg_enum(Status, "status")
SourceType = _pg_enum(Source, "source")


class Entreprise(Base):
    __tablename__ = "entreprise"
    __table_args__ = (
        # Nom unique, insensible à la casse et aux espaces superflus (F1, ADR-004).
        # Écrit sous la forme que Postgres renvoie, sinon Alembic croit que l'index a changé.
        Index("uq_entreprise_name_normalized", text("lower(TRIM(BOTH FROM name))"), unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(2048))
    note: Mapped[str | None] = mapped_column(Text)

    # passive_deletes="all" : l'ORM ne touche pas aux candidatures, Postgres
    # refuse la suppression (ON DELETE RESTRICT) -> 409 côté service (F1).
    applications: Mapped[list[Application]] = relationship(
        back_populates="entreprise",
        passive_deletes="all",
    )


class Application(Base):
    __tablename__ = "application"
    __table_args__ = (CheckConstraint("reminders_count BETWEEN 0 AND 3", name="reminders_count"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    entreprise_id: Mapped[int] = mapped_column(
        ForeignKey("entreprise.id", ondelete="RESTRICT"), index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    url: Mapped[str | None] = mapped_column(String(2048))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[Status] = mapped_column(
        StatusType, default=Status.TO_APPLY, server_default=Status.TO_APPLY.value
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reminders_count: Mapped[int] = mapped_column(default=0, server_default="0")
    last_reminder_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    entreprise: Mapped[Entreprise] = relationship(back_populates="applications")
    # Suppression définitive d'une candidature = suppression de son historique
    # (à revoir si la suppression devient logique, SPEC question ouverte n° 4).
    history: Mapped[list[StatusHistory]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="StatusHistory.changed_at",
    )


class StatusHistory(Base):
    __tablename__ = "status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("application.id", ondelete="CASCADE"), index=True
    )
    from_status: Mapped[Status | None] = mapped_column(StatusType)  # None à la création
    to_status: Mapped[Status] = mapped_column(StatusType)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    source: Mapped[Source] = mapped_column(SourceType)

    application: Mapped[Application] = relationship(back_populates="history")
