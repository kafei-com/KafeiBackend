from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import PyJWTError

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(subject: int, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload
    except PyJWTError:
        return None

