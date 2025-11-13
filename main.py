from fastapi import Depends, FastAPI
from app.api import auth, access_control, business_logic
from app.core.database import engine, Base
from app.config.settings import get_settings

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["auth"])
app.include_router(access_control.router, prefix=settings.API_V1_STR + "/ac", tags=["access-control"], dependencies=[Depends(auth.get_current_user)])
app.include_router(business_logic.router, prefix=settings.API_V1_STR, tags=["business-logic"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Auth System"}
