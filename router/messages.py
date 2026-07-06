import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db, AsyncSessionMaker
from crud.messages import remark_is_read, send_messages_content, get_messages_list

from util.security import SECRET_KEY, ALGORITHM

from models.users import User
from schemas.messages import MessagesCreate
from util.security import get_current_user

router = APIRouter(prefix="/api/messages", tags=["messages"])
# 设置全连接池：{用户id: WebSocket}
# {
#     1: <用户1的WebSocket连接>,
#     2: <用户2的WebSocket连接>,
#     3: <用户3的WebSocket连接>
# }
# 类似于会是个这样的数据字典格式，当用户 1 给用户 2 发消息时，后端在这个字典里查 active_connections.get(2)，如果用户 2 在线，就把消息推过去。
action_connections: dict[int, WebSocket] = {}

# WebSocket不走Http这一套，而且在这个接口中我们需要手动解码token,因为 WebSocket 没有 HTTP 头，不能用 get_current_user
# 同时WebSocket 里不能直接用 Depends(get_db)，要手动创建数据库会话，所以我们也将AsyncSessionMaker引用过来
# WebSocket 收发的是纯文本字符串，要用 json 做字符串↔字典的转换，用于前后端数据传输
@router.websocket("/ws/{token}")
async def send_message_websocket(websocket: WebSocket, token: str):
    try:
        # jwt.decode() 是 JWT 的内置方法，用于解码 token，返回一个字典, 将这个字典命名为 payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])

    except Exception:
        # 如果token过期或者无效就关闭连接
        await websocket.close(code=4001)
        return

    # 接收连接将该用户加入连接池
    await websocket.accept()
    action_connections[user_id] = websocket

    try:
        while True:
            # 接收发送来的消息，如果发送来的是文件或者图片之类的那就用receiver_bytes()
            # data的数据格式是'{"receiver_id": 2, "content": "在吗"}'
            # msg_data则是{"receiver_id": 2, "content": "在吗"}
            data = await websocket.receive_text()
            msg_data = json.loads(data)  # 需要转化为json格式数据

            # 再将接受到的数据存入数据库，在这由于不能使用Depends所以也就只能自己新建一个数据库会话
            async with AsyncSessionMaker() as session:
                msg = await send_messages_content(sender_id=user_id, receiver_id=msg_data["receiver_id"], content=msg_data["content"], db=session)
                await session.commit()

            # 构造返回数据格式
            response = {
                "id": msg.id,
                "sender_id": user_id,
                "receiver_id": msg_data["receiver_id"],
                "content": msg_data["content"],
                "is_read": False,
                "sent_at": msg.sent_at.isoformat()
            }

            # 推送给接受者，并且保证他在线
            receiver_ws = action_connections.get(msg_data["receiver_id"])
            if receiver_ws:
                await receiver_ws.send_text(json.dumps({"type": "new_message", "data": response}, ensure_ascii=False))

            # 回传给发送者自己
            await websocket.send_text(json.dumps({"type": "message_sent", "data": response}, ensure_ascii=False))

    # 断开连接，用户下线之后，receiver_text不会返回数据，而是抛出了WebSocketDisconnect异常
    except WebSocketDisconnect:
        if user_id in action_connections:
            del action_connections[user_id]

# @router.post("/send")
# async def send_messages(data: MessagesCreate, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
#     result = await send_messages_content(user_id, data.receiver_id, data.content, db)
#     return {
#         "code": 200,
#         "message": "发送消息成功",
#         "data": {
#             "id": result.id,
#             "sender_id": user_id,
#             "receiver_id": result.receiver_id,
#             "content": result.content,
#             "is_read": result.is_read,
#             "sent_at": result.sent_at
#         }
#     }


@router.get("/messageslist/{friend_id}")
async def get_messages(friend_id: int, offset: int = 0, limit: int = 50, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = await get_messages_list(db, user_id, friend_id, offset, limit)
    return {
        "code": 200,
        "message": "获取消息列表成功",
        "data": [
            {
                "id": result.id,
                "sender_id": result.sender_id,
                "receiver_id": result.receiver_id,
                "content": result.content,
                "sent_at": result.sent_at.isoformat(),
                "is_read": result.is_read
            } for result in stmt
        ]
    }


@router.put("/remark/{friend_id}")
async def remark_messages(friend_id: int, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await remark_is_read(user_id, friend_id, db)
    return {
        "code": 200,
        "message": "已标记为已读"
    }
