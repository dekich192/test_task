from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

# Association table for User and Role
user_role_association = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), comment="Внешний ключ на таблицу пользователей"),
    Column("role_id", Integer, ForeignKey("roles.id"), comment="Внешний ключ на таблицу ролей"),
    comment="Ассоциативная таблица для связи пользователей и ролей",
)

# Association table for Role, Permission, and Resource
role_permission_association = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), comment="Внешний ключ на таблицу ролей"),
    Column(
        "permission_id", Integer, ForeignKey("permissions.id"), comment="Внешний ключ на таблицу разрешений"
    ),
    Column(
        "element_id",
        Integer,
        ForeignKey("business_elements.id"),
        comment="Внешний ключ на таблицу бизнес-элементов",
    ),
    comment="Ассоциативная таблица для связи ролей, разрешений и бизнес-элементов",
)

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True, comment="Уникальный идентификатор роли")
    name = Column(String, unique=True, index=True, nullable=False, comment="Название роли")
    description = Column(String, comment="Описание роли")
    users = relationship("User", secondary=user_role_association, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True, comment="Уникальный идентификатор разрешения")
    name = Column(String, unique=True, index=True, nullable=False, comment="Название разрешения")

class BusinessElement(Base):
    __tablename__ = "business_elements"
    id = Column(Integer, primary_key=True, index=True, comment="Уникальный идентификатор бизнес-элемента")
    name = Column(String, unique=True, index=True, nullable=False, comment="Название бизнес-элемента")
