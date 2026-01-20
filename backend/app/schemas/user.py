from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdatePassword(BaseModel):
    current_password: str = Field(..., description="Текущий пароль пользователя")
    new_password: str = Field(..., min_length=8, max_length=72, description="Новый пароль (8-72 символа)")

class Token(BaseModel):
    access_token: str
    token_type: str
