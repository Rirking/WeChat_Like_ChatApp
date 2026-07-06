from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str):
    return pwd_context.hash(password)

# 验证用户输入的原始密码是否与数据库中存储的哈希密码匹配,verify 返回的是布尔类型
# plain_password: 原始密码，hashed_password: 存储的哈希密码
def verify_password(plain_password, hashed_password):

    # 将用户输入的密码与存储的哈希密码进行验证，匹配返回True，不匹配返回False
    return pwd_context.verify(plain_password, hashed_password)

"""
 下面使用的是JWT来创建token，并且直接从token中获取user_id
"""

SECRET_KEY = "chat_app_secret_key_26_6_26"      # 签名密钥, JWT 最后一步会用这个密钥给 token "盖个章",只有持有这个密钥的人才能签发和验证 token
ALGORITHM = "HS256"                             # 签名算法, JWT 签名的时候会用这个算法对 token 进行签名, 常用的对称加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 3     # 过期时间 60 * 24 = 1440min 也就是一天，token 签出 72 小时后自动失效，只能重新登录拿新的

security = HTTPBearer()

def create_token(data: dict):
    to_encode = data.copy()
    # python-jose 要求 JWT 的 sub 字段必须是字符串，所以先把 user_id 转成字符串
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})           # update() 是字典内置方法：把新键值对加进去，键重复就覆盖
    # jwt.encode()是将to_encode 转成 JSON 字符串
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# security = HTTPBearer() 是 FastAPI 的安全工具， 它会检查请求头中是否有 Authorization 头，并且 Authorization 头的值以 Bearer 开头
# 找到 → 提取 "Bearer " 后面的内容 → 封装成 HTTPAuthorizationCredentials 对象，没有找到就抛出401异常

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="eyJhbGci..." )，所以credentials.credentials才是真正的token

    token = credentials.credentials
    try:
        # jwt.decode() 是 JWT 的内置方法，用于解码 token，返回一个字典, 将这个字典命名为 payload
        # 其中payload里有一个 "sub" 字段，这个字段的值就是 user_id
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
        # 由于user_id 是 int 类型，如果获取不到应该是抛异常，不会返回 None，所以需要添加一个判断
        item = payload.get("sub")
        if item is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user_id
    except HTTPException:
        # FastAPI 的 HTTPException 直接往上抛，不要再包一层
        raise
    except Exception as e:
        # 把真实错误打印到终端，方便排查；但返回给客户端的用通用提示，避免泄露内部信息
        import traceback
        print(f"[get_current_user 错误] 异常类型: {type(e).__name__},{e}")
        traceback.print_exc()
        raise HTTPException(status_code=401, detail="token 无效或已过期")
