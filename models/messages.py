from sqlalchemy import Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from models.users import Base

class Messages(Base):

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="消息ID")
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="发送者")
    receiver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="接收者")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, comment="对方是否已读")
    sent_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="发送时间")

