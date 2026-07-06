from sqlalchemy import Integer, String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from models.users import Base


class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="申请ID")
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="发送申请的⼈")
    receiver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="收到申请的⼈")
    status: Mapped[str] = mapped_column(
        Enum("pending", "accepted", "rejected"),
        default="pending",
        nullable=False,
        comment="申请状态：pending等待中 / accepted已同意 / rejected已拒绝"
    )
    message: Mapped[str | None] = mapped_column(String(100), comment="验证消息，如：你好我是张三")
    # created_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="申请发送时间")
    # updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now, comment="处理时间")
