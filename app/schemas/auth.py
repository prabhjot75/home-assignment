from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str = Field(..., max_length=80, examples=["prabhjots"])
    email: EmailStr = Field(..., examples=["prabhjot.singh@businessai.com"])

class UserRegister(UserBase):
    password: str = Field(..., min_length=8, examples=["secure_bus_ai123"])

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    user: UserResponse
    token: str