from typing import Optional

from sqlalchemy import DateTime, Integer, String, Enum

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from datetime import datetime

# 创建模型类必须基础DeclarativeBase，但是都同属于property_manager下 为了能够继承
# 同一个DeclarativeBase，所以才设置了一个Base基类
class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class User(Base):

    # 相当于你要创建的表名
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="昵称", default="用户114514")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), default="", comment="头像")
    gender: Mapped[Optional[str]] = mapped_column(Enum("male", "female", "unknown"), default="unknown", comment="性别")
    phone: Mapped[Optional[str]] = mapped_column(String(20), comment="电话号码")
