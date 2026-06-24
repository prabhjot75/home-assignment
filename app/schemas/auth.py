from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=80)
    email: EmailStr

class UserRegister(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    user: UserResponse
    token: str  # <--- Must be exactly 'token' to match user['token'] in tests