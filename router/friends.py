from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.db_config import get_db
from crud.friends import get_friends_list

from models.friends import Friends
from util.security import get_current_user

router = APIRouter(prefix="/api/friends", tags=["friends"])

@router.get("/list")
async def friends_list(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    friends_list = await get_friends_list(user_id, db)

    return {
        "code": 200,
        "message": "获取好友列表成功",
        "data": [
            {
                "id": f.id,
                "username": f.username,
                "nickname": f.nickname,
                "avatar": f.avatar
            } for f in friends_list
        ]
    }



