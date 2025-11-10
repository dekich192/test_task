from pydantic import BaseModel
from typing import List, Optional

# Role Schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True

# Permission Schemas
class PermissionBase(BaseModel):
    name: str

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int

    class Config:
        from_attributes = True

# BusinessElement Schemas
class BusinessElementBase(BaseModel):
    name: str

class BusinessElementCreate(BusinessElementBase):
    pass

class BusinessElement(BusinessElementBase):
    id: int

    class Config:
        from_attributes = True
