from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            patronymic=user.patronymic
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def update_user(self, user: User, user_update: UserUpdate) -> User:
        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user: User) -> User:
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user
