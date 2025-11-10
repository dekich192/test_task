from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.access_control import AccessControlRepository
from app.repositories.user import UserRepository
from pydantic import BaseModel
from app.schemas import access_control as ac_schema
from app.api.auth import get_current_user
from app.models.user import User
from app.models import access_control as ac_model
from typing import List

router = APIRouter()

# Dependency to check if the user has a specific role
def role_checker(required_role: str):
    def checker(current_user: User = Depends(get_current_user)):
        if required_role not in [role.name for role in current_user.roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return checker

def permission_checker(permission_base_name: str, element_name: str):
    def checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), owner_id: int = None):
        required_permissions = [f"{permission_base_name}_all"]
        if owner_id and owner_id == current_user.id:
            required_permissions.append(f"{permission_base_name}_own")

        for role in current_user.roles:
            for perm_name in required_permissions:
                permission = db.query(ac_model.Permission).filter(ac_model.Permission.name == perm_name).first()
                element = db.query(ac_model.BusinessElement).filter(ac_model.BusinessElement.name == element_name).first()
                if not permission or not element: continue

                has_perm = db.query(ac_model.role_permission_association).filter(
                    ac_model.role_permission_association.c.role_id == role.id,
                    ac_model.role_permission_association.c.permission_id == permission.id,
                    ac_model.role_permission_association.c.element_id == element.id
                ).first()
                if has_perm:
                    return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted for this business element"
        )
    return checker

@router.post("/roles", response_model=ac_schema.Role, status_code=status.HTTP_201_CREATED)
def create_role(role: ac_schema.RoleCreate, db: Session = Depends(get_db), admin_user: User = Depends(role_checker("admin"))):
    ac_repo = AccessControlRepository(db)
    db_role = ac_repo.get_role_by_name(role.name)
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    return ac_repo.create_role(role=role)

@router.post("/users/{user_id}/roles/{role_name}")
def assign_role_to_user(user_id: int, role_name: str, db: Session = Depends(get_db), admin_user: User = Depends(role_checker("admin"))):
    user_repo = UserRepository(db)
    ac_repo = AccessControlRepository(db)
    user = user_repo.db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = ac_repo.get_role_by_name(role_name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    ac_repo.assign_role_to_user(user, role)
    return {"message": f"Role '{role_name}' assigned to user '{user.email}'"}


@router.post("/permissions", response_model=ac_schema.Permission, status_code=status.HTTP_201_CREATED)
def create_permission(permission: ac_schema.PermissionCreate, db: Session = Depends(get_db), admin_user: User = Depends(role_checker("admin"))):
    ac_repo = AccessControlRepository(db)
    return ac_repo.create_permission(permission=permission)


@router.post("/elements", response_model=ac_schema.BusinessElement, status_code=status.HTTP_201_CREATED)
def create_business_element(element: ac_schema.BusinessElementCreate, db: Session = Depends(get_db), admin_user: User = Depends(role_checker("admin"))):
    ac_repo = AccessControlRepository(db)
    return ac_repo.create_business_element(element=element)


class RolePermissionRequest(BaseModel):
    permission_name: str
    element_name: str

@router.post("/roles/{role_name}/permissions")
def add_permission_to_role(role_name: str, request: RolePermissionRequest, db: Session = Depends(get_db), admin_user: User = Depends(role_checker("admin"))):
    ac_repo = AccessControlRepository(db)
    role = ac_repo.get_role_by_name(role_name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    permission = ac_repo.get_permission_by_name(request.permission_name)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    element = ac_repo.get_business_element_by_name(request.element_name)
    if not element:
        raise HTTPException(status_code=404, detail="Business element not found")

    ac_repo.add_permission_to_role(role, permission, element)
    return {"message": f"Permission '{request.permission_name}' on element '{request.element_name}' added to role '{role_name}'"}


@router.get("/protected-resource")
def get_protected_resource(current_user: User = Depends(permission_checker("read", "articles"))):
    return {"message": "You have access to the protected resource!", "user": current_user.email}
