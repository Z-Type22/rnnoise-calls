from fastapi import APIRouter, Query, UploadFile
from src.users.schemas import UserRead
from src.users.service import (
    read_users as read_users_service,
    connected_users as connected_users_service,
    search_users as search_users_service,
    upload_avatar as upload_avatar_service,
)
from src.types import AuthorizeSession, DatabaseSession
from src.schemas import Message


router = APIRouter()

@router.get("/", response_model=list[UserRead])
async def read_users(
    user: AuthorizeSession, 
    db: DatabaseSession,
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=5)
):
    return await read_users_service(user, db, page, limit)

@router.get("/connected/{call_uuid}", response_model=list[UserRead])
async def connected_users(
    call_uuid: str, user: AuthorizeSession, db: DatabaseSession
):
    return await connected_users_service(call_uuid, user, db)

@router.get("/me", response_model=UserRead)
async def my_profile(user: AuthorizeSession):
    return user

@router.get("/search", response_model=list[UserRead])
async def search_users(
    user: AuthorizeSession,
    db: DatabaseSession,
    q: str = Query(..., min_length=1, description="Поиск по username")
):
    return await search_users_service(q, user, db)

@router.post("/upload_avatar", response_model=Message)
async def upload_avatar(
    upload_file: UploadFile, user: AuthorizeSession, db: DatabaseSession
):
    return await upload_avatar_service(user, upload_file, db)
