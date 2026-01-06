from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.user import User
from app.services.oauth_client import oauth
from app.utils.jwt import create_access_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["OAuth"])

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(
    request: Request,
    session: Session = Depends(get_session),
):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise Exception("Failed to fetch user info")

    email = user_info["email"]
    sub = user_info["sub"]
    name = user_info.get("name")

    user = session.exec(
        select(User).where(
            User.email == email
        )
    ).first()

    # 🧠 User creation logic
    if not user:
        user = User(
            name=name,
            email=email,
            oauth_provider="google",
            oauth_sub=sub,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    access_token = create_access_token(str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



@router.get("/github/login")
async def github_login(request: Request):
    return await oauth.github.authorize_redirect(
        request,
        settings.GITHUB_REDIRECT_URI
    )

@router.get("/github/callback")
async def github_callback(
    request: Request,
    session: Session = Depends(get_session),
):
    token = await oauth.github.authorize_access_token(request)

    # Fetch GitHub profile
    user_resp = await oauth.github.get("user", token=token)
    profile = user_resp.json()

    # Fetch primary email (GitHub hides email sometimes)
    email_resp = await oauth.github.get("user/emails", token=token)
    emails = email_resp.json()
    primary_email = next(
        (e["email"] for e in emails if e["primary"] and e["verified"]),
        None
    )

    if not primary_email:
        raise HTTPException(status_code=400, detail="Email not available")

    github_id = str(profile["id"])
    name = profile.get("name") or profile.get("login")

    user = session.exec(
        select(User).where(User.email == primary_email)
    ).first()

    if not user:
        user = User(
            name=name,
            email=primary_email,
            oauth_provider="github",
            oauth_sub=github_id,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    access_token = create_access_token(str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
