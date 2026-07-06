from sqlalchemy import select

from models.friends import Friends
from models.users import User

from sqlalchemy.ext.asyncio import AsyncSession

#  获取好友列表
async def get_friends_list(user_id: int, db: AsyncSession):
    """
    SELECT users.id, users.username, users.nickname, users.avatar
    FROM users
    JOIN friends ON friends.friend_id = users.id
    WHERE friends.user_id = 1
    """
    # 如果不加.join(Friends, Friends.friend_id == User.id)就成了联查Friends和Users表中所有符合要求的用户了
    # 也就是笛卡尔积，但是我们要的只是该用户的好友，所以需要Join将两张表按Join里的条件拼起来，保留匹配的之后在选择

    stmt = (select(User.id, User.username, User.nickname, User.avatar)
            .join(Friends, Friends.friend_id == User.id)
            .where(Friends.user_id == user_id))
    result = await db.execute(stmt)
    return result.all()


