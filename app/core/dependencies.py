from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models import access_control as ac_model
from app.models.user import User


def role_checker(required_role: str):
    def checker(current_user: User = Depends(get_current_user)):
        if required_role not in [role.name for role in current_user.roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted",
            )
        return current_user

    return checker


def permission_checker(permission_base_name: str, element_name: str):
    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        owner_id: int = None,
    ):
        required_permissions = [f"{permission_base_name}_all"]
        if owner_id and owner_id == current_user.id:
            required_permissions.append(f"{permission_base_name}_own")

        for role in current_user.roles:
            for perm_name in required_permissions:
                permission = (
                    db.query(ac_model.Permission)
                    .filter(ac_model.Permission.name == perm_name)
                    .first()
                )
                element = (
                    db.query(ac_model.BusinessElement)
                    .filter(ac_model.BusinessElement.name == element_name)
                    .first()
                )
                if not permission or not element:
                    continue

                has_perm = (
                    db.query(ac_model.role_permission_association)
                    .filter(
                        ac_model.role_permission_association.c.role_id == role.id,
                        ac_model.role_permission_association.c.permission_id
                        == permission.id,
                        ac_model.role_permission_association.c.element_id == element.id,
                    )
                    .first()
                )
                if has_perm:
                    return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted for this business element",
        )

    return checker
