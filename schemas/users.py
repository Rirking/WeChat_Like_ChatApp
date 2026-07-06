from typing import Optional

from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    nickname: str

class UserResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None  # male / female / unknown
    phone: Optional[str] = None
