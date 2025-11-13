from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from .access_control import user_role_association
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="Уникальный идентификатор пользователя")
    first_name = Column(String, nullable=True, comment="Имя пользователя")
    last_name = Column(String, nullable=True, comment="Фамилия пользователя")
    patronymic = Column(String, nullable=True, comment="Отчество пользователя")
    email = Column(String, unique=True, index=True, nullable=False, comment="Электронная почта пользователя (логин)")
    hashed_password = Column(String, nullable=False, comment="Хэшированный пароль пользователя")
    is_active = Column(Boolean, default=True, comment="Флаг активности пользователя")
    created_at = Column(DateTime, server_default=func.now(), comment="Время создания записи")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="Время последнего обновления записи")
    roles = relationship(
        "Role", secondary=user_role_association, back_populates="users"
    )
