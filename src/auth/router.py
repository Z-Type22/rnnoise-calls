from fastapi import APIRouter, Depends, Response, Cookie
from src.auth.schemas import UserCreate, UserLogin
from src.users.schemas import UserRead
from src.auth.service import (
    create_user, 
    authenticate_user, 
    set_tokens,
    set_logout,
    get_access_token
)
from src.auth.schemas import TokensSchema
from src.types import DatabaseSession
from src.config import settings
from src.schemas import Message
from typing import Annotated


router = APIRouter()

@router.post("/registration", response_model=UserRead)
async def registration(user: UserCreate, db: DatabaseSession):
    return await create_user(user, db)

@router.post("/login", response_model=TokensSchema)
async def login(
    response: Response,
    user: Annotated[UserLogin, Depends(authenticate_user)],
):
    return await set_tokens(response, user)

@router.post("/refresh")
async def refresh(
    response: Response,
    refresh_token: Annotated[
        str | None, 
        Cookie(alias=settings.cookies.refresh_cookie_name)
    ] = None,
):
    return await get_access_token(response, refresh_token)

@router.post("/logout", response_model=Message)
async def logout(
    response: Response,
    db: DatabaseSession,
    access_token: Annotated[
        str | None, 
        Cookie(alias=settings.cookies.access_cookie_name)
    ] = None,
    refresh_token: Annotated[
        str | None, 
        Cookie(alias=settings.cookies.refresh_cookie_name)
    ] = None,
):
    return await set_logout(response, access_token, refresh_token, db)
