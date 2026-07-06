from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette import status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update

from config.db_config import get_db
from models.users import User
from schemas.users import UserLogin, UserRegister, UserResponse, UserUpdate
from util.security import verify_password, create_token, get_current_user

from crud.users import get_user_by_username, create_user, update_user_info

import os
import uuid

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register")
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_username(user_data.username, db)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    user = await create_user(user_data, db)

    # 登录完直接注册，所以不用返回token再次验证用户
    # token = create_token({"sub": user.id})
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "userinfo": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "gender": user.gender,
                "phone": user.phone
            }
        }
    }

@router.post("/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await get_user_by_username(user_data.username, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在")
    if not verify_password(user_data.password, result.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码错误")

    token = create_token({"sub": result.id})

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": token,
            "userinfo": {
                "id": result.id,
                "username": result.username,
                "nickname": result.nickname
            }
        }
    }

@router.get("/info")
async def get_user_info(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {
        "code": 200,
        "message": "获取用户信息成功",
        "data": {
            "userinfo": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "gender": user.gender,
                "phone": user.phone
            }
        }
    }

@router.get("/search")
async def search_user(username, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(and_(User.username == username, User.id != user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return {
            "code": 404,
            "message": "查无此用户",
            "data": None
        }

    return {
        "code": 200,
        "message": "搜索成功",
        "data": {
            "userinfo": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "gender": user.gender,
                "phone": user.phone
            }
        }
    }

@router.put("/update")
async def update_user(
    data: UserUpdate,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await update_user_info(user_id, db, data)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {
        "code": 200,
        "message": "更新成功",
        "data": {
            "userinfo": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "gender": user.gender,
                "phone": user.phone
            }
        }
    }

# 只管收文件 + 存盘 + 返回 URL，不更新数据库
@router.post("/upload_avatar")
async def upload_avatar(file: UploadFile = File(...), user_id: int = Depends(get_current_user)):
    upload_dir = "/var/www/html/property_manager/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    avatar_url = f"/property_manager/uploads/{filename}"

    return {
        "code": 200,
        "message": "头像上传成功",
        "data": {"avatar": avatar_url}
    }
