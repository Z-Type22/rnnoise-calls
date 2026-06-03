from fastapi import APIRouter, WebSocket, status
from src.calls.service import (
    offer as offer_service,
    read_calls as read_calls_service,
    invited_calls as invited_calls_service,
    retrieve_call as retrieve_call_service,
    create_call as create_call_service,
    delete_call as delete_call_service,
    add_callee as add_callee_service,
    remove_callee as remove_callee_service
)
from src.calls.schemas import CallRead, CalleeSchema, CallCreate
from src.calls.responses import CALLEE_RESPONSES
from src.types import DatabaseSession, AuthorizeSession


router = APIRouter()

@router.websocket("/offer")
async def offer(websocket: WebSocket, user: AuthorizeSession, db: DatabaseSession):
    return await offer_service(websocket, user, db)

@router.get("/", response_model=list[CallRead])
async def read_calls(user: AuthorizeSession, db: DatabaseSession):
    return await read_calls_service(user, db)

@router.get("/invited", response_model=list[CallRead])
async def invited_calls(user: AuthorizeSession, db: DatabaseSession):
    return await invited_calls_service(user, db)

@router.get("/{call_id}", response_model=CallRead)
async def retrieve_call(call_id: int, user: AuthorizeSession, db: DatabaseSession):
    return await retrieve_call_service(call_id, user, db)

@router.post("/", response_model=CallRead)
async def create_call(data: CallCreate, user: AuthorizeSession, db: DatabaseSession):
    return await create_call_service(data, user, db)

@router.delete(
    "/{call_id}", 
    responses={status.HTTP_204_NO_CONTENT: {"description": "No content"}},
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_call(call_id: int, user: AuthorizeSession, db: DatabaseSession):
    return await delete_call_service(call_id, user, db)

@router.post("/add_callee", response_model=CallRead, responses=CALLEE_RESPONSES)
async def add_callee(data: CalleeSchema, user: AuthorizeSession, db: DatabaseSession):
    return await add_callee_service(data, user, db)

@router.post("/remove_callee", response_model=CallRead)
async def remove_callee(data: CalleeSchema, user: AuthorizeSession, db: DatabaseSession):
    return await remove_callee_service(data, user, db)
