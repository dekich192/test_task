from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import access_control as ac_model
from app.models import user as user_model
from app.schemas import access_control as ac_schema

class AccessControlRepository:
    def __init__(self, db: Session):
        self.db = db

    # Role methods
    def create_role(self, role: ac_schema.RoleCreate) -> ac_model.Role:
        db_role = ac_model.Role(**role.model_dump())
        try:
            self.db.add(db_role)
            self.db.commit()
            self.db.refresh(db_role)
            return db_role
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_role_by_name(self, name: str) -> ac_model.Role | None:
        return self.db.query(ac_model.Role).filter(ac_model.Role.name == name).first()

    # User-Role assignment
    def assign_role_to_user(self, user: user_model.User, role: ac_model.Role):
        try:
            user.roles.append(role)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_permission_by_name(self, name: str) -> ac_model.Permission | None:
        return self.db.query(ac_model.Permission).filter(ac_model.Permission.name == name).first()

    def get_business_element_by_name(self, name: str) -> ac_model.BusinessElement | None:
        return self.db.query(ac_model.BusinessElement).filter(ac_model.BusinessElement.name == name).first()


    # Permission methods
    def create_permission(
        self, permission: ac_schema.PermissionCreate
    ) -> ac_model.Permission:
        db_permission = ac_model.Permission(**permission.model_dump())
        try:
            self.db.add(db_permission)
            self.db.commit()
            self.db.refresh(db_permission)
            return db_permission
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    # Resource methods
    def create_business_element(
        self, element: ac_schema.BusinessElementCreate
    ) -> ac_model.BusinessElement:
        db_element = ac_model.BusinessElement(**element.model_dump())
        try:
            self.db.add(db_element)
            self.db.commit()
            self.db.refresh(db_element)
            return db_element
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    # Role-Permission-Resource assignment
    def add_permission_to_role(
        self, role: ac_model.Role, permission: ac_model.Permission, element: ac_model.BusinessElement
    ):
        try:
            insert_stmt = ac_model.role_permission_association.insert().values(
                role_id=role.id,
                permission_id=permission.id,
                element_id=element.id,
            )
            self.db.execute(insert_stmt)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
