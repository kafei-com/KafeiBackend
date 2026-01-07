from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from app.services.auth_service import AuthService
from app.db.database import get_session
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse, LoginRequest, TokenResponse
# from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
def register_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
):
    return AuthService.register_user(payload, session)


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: LoginRequest,
    session: Session = Depends(get_session),
):
    return AuthService.login_user(payload, session)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}