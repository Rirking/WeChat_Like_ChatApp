from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from models.friends import Friends
from models.friends_request import FriendRequest

# 发送申请
async def add_friends(user_id: int, friend_id: int, messages: str | None, db: AsyncSession):
    # 不能添加自己为好友
    if user_id == friend_id:
        raise HTTPException(status_code=404, detail="不能添加自己为好友")

    # 已经是好友了不用添加
    stmt = select(Friends).where(and_(Friends.user_id == user_id, Friends.friend_id == friend_id))
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="你们已经是好友了")

    request = FriendRequest(sender_id=user_id, receiver_id=friend_id, message=messages or "", status="pending")
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request

# 获取申请好友列表
async def get_request_list(user_id: int, db: AsyncSession):
    stmt = select(
        FriendRequest.id,
        FriendRequest.sender_id,
        FriendRequest.receiver_id,
        FriendRequest.status,
        FriendRequest.message,
        FriendRequest.created_at,
    ).where(
        FriendRequest.receiver_id == user_id,
        FriendRequest.status == "pending"
    ).order_by(FriendRequest.created_at.desc())

    result = await db.execute(stmt)
    return result.all()

async def delete_request(request_id: int, user_id: int, db: AsyncSession):
    request = await db.get(FriendRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="申请不存在")

    stmt = delete(FriendRequest).where(FriendRequest.id == request_id)
    result = await db.execute(stmt)
    await db.commit()
    return result


# 处理申请, 先查看是否有这个请求，同意之后再将双方都插入friend表
async def fix_request_status(request_id: int, user_id: int, action: str, db: AsyncSession):
    request = await db.get(FriendRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="申请不存在")

    if request.receiver_id != user_id:
        raise HTTPException(status_code=403, detail="无权处理他人的申请")

    if action == "accept":
        request.status = "accepted"
        db.add(Friends(user_id=request.sender_id, friend_id=request.receiver_id))
        db.add(Friends(user_id=request.receiver_id, friend_id=request.sender_id))
    elif action == "reject":
        request.status = "rejected"
    await db.commit()
    await db.refresh(request)



