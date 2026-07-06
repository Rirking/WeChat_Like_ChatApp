from sqlalchemy import Integer, ForeignKey, Enum, String, DECIMAL, Date
from sqlalchemy.orm import Mapped, mapped_column
from models import users
from datetime import date, datetime
from models.users import Base

class Friends(Base):

    __tablename__ = "friends"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, comment="ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    added_at: Mapped[datetime] = mapped_column(default=datetime.now, comment="成为好友的时间")
    friend_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="好友ID")

    # created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    # updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

