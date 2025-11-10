from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app.schemas.user import TokenData
from datetime import timedelta
from app.schemas.user import Token
from app.core.security import verify_password, create_access_token
from app.models.user import User as UserModel
from app.config.settings import get_settings
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, User, UserUpdate
from app.repositories.user import UserRepository

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        settings = get_settings()
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    db_user = user_repo.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return user_repo.create_user(user=user)


@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.put("/users/me", response_model=User)
def update_user_me(user_update: UserUpdate, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return user_repo.update_user(user=current_user, user_update=user_update)


@router.delete("/users/me", response_model=User)
def delete_user_me(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return user_repo.delete_user(user=current_user)


@router.post("/logout")
def logout(current_user: UserModel = Depends(get_current_user)):
    # В stateless JWT-архитектуре logout обрабатывается на клиенте удалением токена.
    # Этот эндпоинт здесь для полноты API.
    return {"message": "Successfully logged out"}
