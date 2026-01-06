from fastapi import HTTPException, status
from sqlmodel import select, Session

from app.models.user import User
from app.schemas.auth import UserCreate
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token

class AuthService:

    @staticmethod
    def register_user(payload: UserCreate, session: Session) -> User:
        existing_user = session.exec(
            select(User).where(User.email == payload.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user = User(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            hashed_password=hash_password(payload.password),
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    @staticmethod
    def login_user(payload, session: Session):
        user = session.exec(
            select(User).where(User.email == payload.email)
        ).first()

        if user.oauth_provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use social login for this account"
            )

        if not user or not verify_password(
            payload.password,
            user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = create_access_token(str(user.id))

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
