from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update

from config.db_config import get_db
from models.friends import Friends
from models.users import User
from schemas.users import UserRegister, UserUpdate
from util.security import get_hashed_password

# 验证用户是否在数据库中
async def get_user_by_username(username: str, db: AsyncSession):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(user_data: UserRegister, db: AsyncSession):
    hashed_password = get_hashed_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password, nickname=user_data.nickname)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 创建一个用户就和我的测试用户捆绑为好友，两边都要这样
    db.add(Friends(user_id=user.id, friend_id=1))
    db.add(Friends(user_id=1, friend_id=user.id))

    await db.commit()
    return user


async def update_user_info(user_id: int, db: AsyncSession, user_data: UserUpdate):
    """
        model_dump(exclude_none=True)：把 UserUpdate 转成字典，None 字段自动跳过
        比如用户只填了 nickname，avatar/gender/phone 都为 None → 只有 {"nickname": "阿杰"}
        如果啥都没传入就直接跳出，不管了
    """
    update_data = user_data.model_dump(exclude_none=True)

    if not update_data:
        return None

    stmt = update(User).where(User.id == user_id).values(**update_data)
    await db.execute(stmt)
    await db.commit()

    # 返回更新后的用户信息
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
