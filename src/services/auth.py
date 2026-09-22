import datetime

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from src.config import Config
from src.extensions import db
from src.models import User


def register_user(
    username: str,
    email: str,
    password: str,
) -> dict:
    """Registra un nuevo usuario en la plataforma."""

    if User.query.filter_by(username=username).first():
        return {
            "success": False,
            "error": "El nombre de usuario ya está registrado.",
        }

    if User.query.filter_by(email=email).first():
        return {
            "success": False,
            "error": "El email ya está registrado.",
        }

    hashed = generate_password_hash(password)

    user = User(
        username=username,
        email=email,
        password_hash=hashed,
        elo_rating=1200,
    )

    db.session.add(user)
    db.session.commit()

    return {
        "success": True,
        "user": user.to_dict(),
    }


def authenticate_user(
    username_or_email: str,
    password: str,
) -> dict:
    """Autentica las credenciales de un usuario y genera un token JWT."""

    user = User.query.filter(
        (User.username == username_or_email)
        | (User.email == username_or_email)
    ).first()

    if not user or not check_password_hash(
        user.password_hash,
        password,
    ):
        return {
            "success": False,
            "error": "Credenciales inválidas.",
        }

    # Generar Token JWT con 24 horas de validez
    payload = {
        "user_id": str(user.id),
        "username": user.username,
        "exp": (
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=24)
        ),
    }

    token = jwt.encode(
        payload,
        Config.SECRET_KEY,
        algorithm="HS256",
    )

    return {
        "success": True,
        "token": token,
        "user": user.to_dict(),
    }