from pydantic import BaseModel, EmailStr
from typing import Optional

# Схема для создания пользователя (регистрация)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None

# Схема для обновления данных пользователя
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None

# Базовая схема для пользователя (для возврата в API)
class UserBase(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None

    class Config:
        from_attributes = True

# Схема для отображения пользователя
class User(UserBase):
    pass

# Схема для токена
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
