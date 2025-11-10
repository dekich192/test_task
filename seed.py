import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models import access_control as ac_model
from app.models.access_control import Role, Permission, Resource
from app.core.security import get_password_hash

# --- Initial Data ---
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

ROLES = ["admin", "user"]
PERMISSIONS = [
    "create", 
    "read_own", "read_all", 
    "update_own", "update_all", 
    "delete_own", "delete_all"
]
BUSINESS_ELEMENTS = ["articles", "users"]

async def seed_data():
    db = SessionLocal()
    try:
        print("Seeding database...")

        # Create Roles
        for role_name in ROLES:
            if not db.query(Role).filter(Role.name == role_name).first():
                db.add(Role(name=role_name))

        # Create Permissions
        for perm_name in PERMISSIONS:
            if not db.query(Permission).filter(Permission.name == perm_name).first():
                db.add(Permission(name=perm_name))

        # Create Resources
        for res_name in BUSINESS_ELEMENTS:
            if not db.query(ac_model.BusinessElement).filter(ac_model.BusinessElement.name == res_name).first():
                db.add(ac_model.BusinessElement(name=res_name))
        
        db.commit()

        # Create Admin User
        admin_user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if not admin_user:
            hashed_password = get_password_hash(ADMIN_PASSWORD)
            admin_user = User(email=ADMIN_EMAIL, hashed_password=hashed_password)
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            # Assign admin role
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                admin_user.roles.append(admin_role)
                db.commit()
            print(f"Admin user '{ADMIN_EMAIL}' created with password '{ADMIN_PASSWORD}'")
        else:
            print("Admin user already exists.")

        # --- Assigning permissions to roles ---
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        user_role = db.query(Role).filter(Role.name == "user").first()

        if admin_role:
            for element_name in BUSINESS_ELEMENTS:
                element = db.query(ac_model.BusinessElement).filter(ac_model.BusinessElement.name == element_name).first()
                if not element: continue
                for perm_name in [p for p in PERMISSIONS if 'all' in p or p == 'create']:
                    permission = db.query(Permission).filter(Permission.name == perm_name).first()
                    if permission:
                        existing_perm = db.execute(ac_model.role_permission_association.select().where(ac_model.role_permission_association.c.role_id == admin_role.id, ac_model.role_permission_association.c.permission_id == permission.id, ac_model.role_permission_association.c.element_id == element.id)).first()
                        if not existing_perm:
                            db.execute(ac_model.role_permission_association.insert().values(role_id=admin_role.id, permission_id=permission.id, element_id=element.id))
            print("Assigned full admin permissions to 'admin' role.")

        if user_role:
            articles_element = db.query(ac_model.BusinessElement).filter(ac_model.BusinessElement.name == "articles").first()
            if articles_element:
                user_perms = ["create", "read_own", "update_own", "delete_own"]
                for perm_name in user_perms:
                    permission = db.query(Permission).filter(Permission.name == perm_name).first()
                    if permission:
                        existing_perm = db.execute(ac_model.role_permission_association.select().where(ac_model.role_permission_association.c.role_id == user_role.id, ac_model.role_permission_association.c.permission_id == permission.id, ac_model.role_permission_association.c.element_id == articles_element.id)).first()
                        if not existing_perm:
                            db.execute(ac_model.role_permission_association.insert().values(role_id=user_role.id, permission_id=permission.id, element_id=articles_element.id))
            print("Assigned user permissions on 'articles' to 'user' role.")
        
        db.commit()
        print("Database seeding complete.")

    finally:
        db.close()

if __name__ == "__main__":
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    asyncio.run(seed_data())
