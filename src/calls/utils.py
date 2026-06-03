from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from src.users.models import User
from src.calls.models import Call
from src.calls.schemas import CalleeSchema
from src.types import Peer


async def get_user_and_call(
    data: CalleeSchema, user: User, db: AsyncSession
) -> tuple[User, Call]:
    callee = await db.scalar(select(User).where(User.id == data.callee_id))
    if not callee:
        raise HTTPException(status_code=404, detail="User not found.")
    
    call = await db.execute(select(Call).where(Call.id == data.call_id, user.id == Call.caller_id))
    if not call:
        raise HTTPException(status_code=404, detail="Call not found.")
    
    return callee, call

async def cleanup_peer(rooms: dict[str, list[Peer]], call_id: str, user_id: int) -> None:
    if call_id not in rooms: return

    peer_to_remove = None
    for peer in rooms[call_id]:
        if peer["user_id"] == user_id:
            peer_to_remove = peer
            break
        
    if not peer_to_remove: return

    pc = peer_to_remove["pc"]

    for peer in rooms[call_id]:
        if peer["pc"] != pc:
            try:
                peer["transceiver"].sender.replaceTrack(None)
            except Exception:
                pass

    rooms[call_id] = [peer for peer in rooms[call_id] if peer["pc"] != pc]
    if not rooms[call_id]:
        del rooms[call_id]

    await pc.close()
    print(f"[{call_id}] peer {user_id} cleaned up")
