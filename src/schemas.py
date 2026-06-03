from pydantic import BaseModel
from typing import Literal


class Message(BaseModel):
    detail: Literal["Success.", "Logged out."]
