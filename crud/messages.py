from models.messages import Messages
from schemas.messages import MessagesOut, MessagesCreate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, update


# 发送消息
async def send_messages_content(sender_id: int, receiver_id: int, content: str, db: AsyncSession):
    stmt = Messages(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(stmt)
    await db.commit()
    await db.refresh(stmt)
    return stmt


# 获取聊天记录
async def get_messages_list(db: AsyncSession, user_id: int, friend_id: int, offset: int = 0, limit: int = 50):
    """
        SELECT * FROM messages
        WHERE (sender_id = :user_id AND receiver_id = :friend_id)
           OR (sender_id = :friend_id AND receiver_id = :user_id)
        ORDER BY sent_at ASC
        LIMIT :limit OFFSET :offset
    """
    stmt = (
            select(Messages)
            .where(
                or_(
                    and_(Messages.sender_id == user_id, Messages.receiver_id == friend_id),
                    and_(Messages.sender_id == friend_id, Messages.receiver_id == user_id)
                )
            )
            .order_by(Messages.sent_at)
            .offset(offset).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

# 标记是否已读
async def remark_is_read(user_id: int, friend_id: int, db: AsyncSession):
    """
    标记已读的消息是将接收者为第一视角，所以这个消息的接收者就是user_id
    UPDATE Messages SET is_read=True WHERE receiver=:user_id AND sender_id=:friend_id AND is_read=False
    """
    stmt = (
        update(Messages)
        .where(
            and_(
                Messages.receiver_id == user_id, Messages.sender_id == friend_id, Messages.is_read == False
            )
        ).values(is_read=True)
    )
    await db.execute(stmt)
    await db.commit()
