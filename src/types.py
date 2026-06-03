from typing import TypedDict, Literal, Annotated
from fastapi import Depends, WebSocket
from aiortc import RTCPeerConnection, RTCRtpTransceiver
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.models import User
from src.auth.jwt_service import authorize
from src.database import get_db


class Payload(TypedDict):
    sub: str
    type: Literal["access", "refresh"]
    jti: str
    now: datetime
    exp: datetime


class Errors(TypedDict):    
    loc: list[str]
    msg: str
    type: str
    input: str
    ctx: dict


class Peer(TypedDict):
    ws: WebSocket
    pc: RTCPeerConnection
    user: User
    user_id: int
    transceiver: RTCRtpTransceiver


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
AuthorizeSession = Annotated[User, Depends(authorize)]
