from aiortc import RTCPeerConnection, RTCSessionDescription, AudioStreamTrack
from aiortc.contrib.media import MediaRelay
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
from src.users.models import User
from src.calls.models import Call
from src.calls.denoise import FrameSplitterTrack
from src.calls.schemas import CalleeSchema, CallCreate, UserRead
from src.calls.utils import get_user_and_call, cleanup_peer
from src.types import Peer


relay: MediaRelay = MediaRelay()
rooms: dict[str, list[Peer]] = {} 

async def offer(websocket: WebSocket, user: User, db: AsyncSession) -> None:
    await websocket.accept()
    data = await websocket.receive_json()
    call_id = data["call_id"]

    call = await db.scalar(select(Call).where(Call.uuid == call_id))
    if not call or (user.id != call.caller_id and user not in call.callees):
        await websocket.close(code=1008)
        return

    pc = RTCPeerConnection()
    audio_transceiver = pc.addTransceiver("audio", direction="sendrecv")

    peer: Peer = {
        "ws": websocket,
        "pc": pc,
        "user": user,
        "user_id": user.id,
        "transceiver": audio_transceiver,
    }
    rooms.setdefault(call_id, []).append(peer)

    print(f"[{call_id}] peer {user.id} connected, total: {len(rooms[call_id])}")

    for p in rooms[call_id]:
        await p["ws"].send_json({
            "event": "peer_joined",
            "users": [
                UserRead.model_validate(p["user"]).model_dump()
                for p in rooms[call_id]
            ],
        })

    @pc.on("track")
    def on_track(track: AudioStreamTrack):
        if track.kind != "audio": return

        print(f"[{call_id}] audio track from {user.id}")
        track = FrameSplitterTrack(track)
        relayed = relay.subscribe(track)

        for p in rooms[call_id]:
            if p["pc"] != pc:
                try:
                    p["transceiver"].sender.replaceTrack(relayed)
                except Exception:
                    pass

    @pc.on("connectionstatechange")
    async def on_connection_state_change():
        print(f"[{call_id}] pc {user.id} state {pc.connectionState}")
        if pc.connectionState in ("failed", "disconnected", "closed"):
            await cleanup_peer(rooms, call_id, user.id)

    await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    await websocket.send_json({
        "event": "answer",
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
    })

    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"[{call_id}] websocket disconnected {user.id}")
    finally:
        await cleanup_peer(rooms, call_id, user.id)

        for p in rooms.get(call_id, []):
            if p["user_id"] != user.id:
                try:
                    await p["ws"].send_json({
                        "event": "peer_left",
                        "user_id": user.id,
                    })
                except Exception:
                    pass

        await pc.close()

async def read_calls(user: User, db: AsyncSession) -> list[Call]:
    calls = (await db.scalars(select(Call).where(Call.caller_id == user.id))).all()
    return calls

async def invited_calls(user: User, db: AsyncSession) -> list[Call]:
    calls = (await db.scalars(select(Call).where(Call.callees.any(id=user.id)))).all()
    return calls

async def retrieve_call(call_id: int, user: User, db: AsyncSession) -> Call:
    call = (await db.scalars(
        select(Call).where(Call.caller_id == user.id, Call.id == call_id)
    )).all()
    if not call:
        raise HTTPException(detail="Call not found.", status_code=404)
    return call

async def create_call(data: CallCreate, user: User, db: AsyncSession) -> Call:    
    call = Call(caller_id=user.id, title=data.title)

    db.add(call)
    await db.commit()
    await db.refresh(call)

    return call

async def delete_call(call_id: int, user: User, db: AsyncSession) -> None:
    call = (await db.scalars(
        select(Call).where(Call.id == call_id,Call.caller_id == user.id)
    )).all()
    if not call:
        raise HTTPException(detail="Call not found.", status_code=404)

    await db.delete(call)
    await db.commit()

async def add_callee(data: CalleeSchema, user: User, db: AsyncSession) -> Call:
    callee, call = await get_user_and_call(data, user, db)
    
    if callee in call.callees:
        return JSONResponse(
            content={"detail": "User already in call."}, status_code=208
        )

    call.callees.append(callee)
    db.add(call)
    await db.commit()
    await db.refresh(call)

    return call

async def remove_callee(data: CalleeSchema, user: User, db: AsyncSession) -> Call:
    callee, call = await get_user_and_call(data, user, db)
    
    if callee in call.callees:
        call.callees.remove(callee)
        db.add(call)
        await db.commit()
        await db.refresh(call)

    return call
