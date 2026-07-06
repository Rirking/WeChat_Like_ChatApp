from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud.friends_request import add_friends, delete_request, get_request_list, fix_request_status
from schemas.friends_request import FriendRequestCreate, FriendRequestHandle
from util.security import get_current_user

router = APIRouter(prefix="/api/friends_request", tags=["friends_request"])

# 发送好友请求，user_id为发送者，data获取的就是接收者的user_id以及发送着发送的message
@router.post("/add")
async def add_friends_list(data: FriendRequestCreate, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    await add_friends(user_id, data.receiver_id, data.message, db)
    return {
        "code": 200,
        "message": "添加好友成功",
        "data": None
    }

@router.get("/list")
async def get_requests(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    request = await get_request_list(user_id, db)

    return {
        "code": 200,
        "message": "获取申请好友列表成功",
        "data": [
            {
                "id": r.id,
                "sender_id": r.sender_id,
                "receiver_id": r.receiver_id,
                "status": r.status,
                "message": r.message,
                "created_at": r.created_at.isoformat() if r.created_at else None
            } for r in request
        ]
    }


@router.put("/status")
async def fix_status(data: FriendRequestHandle, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await fix_request_status(data.request_id, user_id, data.action, db)
    act = "同意" if data.action == "accept" else "拒绝"
    return {
        "code": 200,
        "message": f"已{act}该用户好友申请",
        "data": None
    }

@router.delete("/delete")
async def delete_request_list(data: FriendRequestHandle, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_request(data.request_id, user_id, db)
    return {
        "code": 200,
        "message": "删除申请成功",
        "data": None
    }

