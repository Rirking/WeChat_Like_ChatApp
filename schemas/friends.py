from typing import Optional

from pydantic import BaseModel

class FriendInfo(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None

