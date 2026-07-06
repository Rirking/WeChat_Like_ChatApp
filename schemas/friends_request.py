from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from schemas.friends import FriendInfo


# 前端点击添加好友，输入用户的username之后给请求添加好友，之后验证信息
class FriendRequestCreate(BaseModel):
    receiver_id: int                # 对方的用户ID，前端从搜索结果里拿
    message: Optional[str] = None

# 查看好友申请列表
class FriendRequestList(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    message: Optional[str] = None
    created_at: Optional[datetime] = None

    sender: Optional[FriendInfo] = None  # from schemas.friends
    receiver: Optional[FriendInfo] = None

# 处理好友申请列表
class FriendRequestHandle(BaseModel):
    request_id: int         # 处理哪条申请（friend_requests表的id）
    action: str             # "accept" 或 "reject"



