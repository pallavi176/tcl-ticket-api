"""Token issuance (demo — replace with real IdP in production)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from app.api.deps import get_settings_dep
from app.config import Settings
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(BaseModel):
    """OAuth2-style token response."""

    access_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field(default="bearer")


@router.post("/token", response_model=TokenResponse, summary="Obtain JWT (demo user)")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> TokenResponse:
    """Issue JWT when credentials match configured demo user."""
    if form_data.username != settings.demo_username or form_data.password != settings.demo_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Incorrect username or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(subject=form_data.username)
    return TokenResponse(access_token=token)
