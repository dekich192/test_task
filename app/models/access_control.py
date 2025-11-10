from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

# Association table for User and Role
user_role_association = Table(
    'user_role', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

# Association table for Role, Permission, and Resource
role_permission_association = Table(
    'role_permission', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id')),
    Column('element_id', Integer, ForeignKey('business_elements.id'))
)

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    users = relationship("User", secondary=user_role_association, back_populates="roles")

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

class BusinessElement(Base):
    __tablename__ = 'business_elements'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
