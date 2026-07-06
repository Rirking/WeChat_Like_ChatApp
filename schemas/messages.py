from datetime import datetime

from pydantic import BaseModel

class MessagesCreate(BaseModel):
    receiver_id: int
    content: str

class MessagesOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    sent_at: datetime
    is_read: bool
