import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.extensions import db


def get_utc_now():
    return datetime.now(timezone.utc)


player_teams = Table(
    "player_teams",
    db.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column(
        "player_id",
        UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "team_id",
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("start_year", Integer, nullable=True),
    Column("end_year", Integer, nullable=True),
)

player_coaches = Table(
    "player_coaches",
    db.metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column(
        "player_id",
        UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "coach_id",
        UUID(as_uuid=True),
        ForeignKey("coaches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "team_id",
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=True,
    ),
)

team_competitions = Table(
    "team_competitions",
    db.metadata,
    Column(
        "team_id",
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "competition_id",
        UUID(as_uuid=True),
        ForeignKey("competitions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("season", String(20), nullable=True),
)


# ==========================================
# ENTIDAD: USUARIO Y COMPETITIVIDAD
# ==========================================

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    elo_rating: Mapped[int] = mapped_column(
        Integer,
        default=1200,
        nullable=False,
        index=True,
    )
    matches_played: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    wins: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    losses: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "elo_rating": self.elo_rating,
            "stats": {
                "matches_played": self.matches_played,
                "wins": self.wins,
                "losses": self.losses,
            },
            "created_at": self.created_at.isoformat(),
        }


# ==========================================
# NODOS DEL GRAFO FUTBOLÍSTICO
# ==========================================

class Player(db.Model):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    nationality: Mapped[str] = mapped_column(
        String(60),
        nullable=True,
    )
    position: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
    )
    image_url: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
    )

    teams = relationship(
        "Team",
        secondary=player_teams,
        back_populates="players",
    )
    coaches = relationship(
        "Coach",
        secondary=player_coaches,
        back_populates="players",
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "nationality": self.nationality,
            "position": self.position,
            "image_url": self.image_url,
        }


class Team(db.Model):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    country: Mapped[str] = mapped_column(
        String(60),
        nullable=True,
    )
    logo_url: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
    )

    players = relationship(
        "Player",
        secondary=player_teams,
        back_populates="teams",
    )
    competitions = relationship(
        "Competition",
        secondary=team_competitions,
        back_populates="teams",
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "country": self.country,
            "logo_url": self.logo_url,
        }


class Coach(db.Model):
    __tablename__ = "coaches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    nationality: Mapped[str] = mapped_column(
        String(60),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
    )

    players = relationship(
        "Player",
        secondary=player_coaches,
        back_populates="coaches",
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "nationality": self.nationality,
        }


class Competition(db.Model):
    __tablename__ = "competitions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
    )

    teams = relationship(
        "Team",
        secondary=team_competitions,
        back_populates="competitions",
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type,
        }