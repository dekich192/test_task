from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from pydantic import BaseModel

from app.api.access_control import permission_checker
from app.core.database import SessionLocal
from app.models.user import User

router = APIRouter()

# --- Mock Data ---
mock_articles = [
    {"id": 1, "title": "FastAPI for Beginners", "content": "...", "owner_id": 1}, # Admin's article
    {"id": 2, "title": "Advanced SQLAlchemy", "content": "...", "owner_id": 2}, # Another user's article
]

class Article(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int

# --- Mock API Endpoints for Articles ---

@router.get("/articles", response_model=List[Article])
def get_articles_list(current_user: User = Depends(permission_checker("read", "articles"))):
    # This endpoint is simplified. A real implementation would check for 'read_own' 
    # and filter the list, or allow full access for 'read_all'.
    return mock_articles

@router.post("/articles", response_model=Article, status_code=status.HTTP_201_CREATED)
def create_article(current_user: User = Depends(permission_checker("create", "articles"))):
    new_article = {"id": len(mock_articles) + 1, "title": "New Article", "content": "...", "owner_id": current_user.id}
    mock_articles.append(new_article)
    return new_article

@router.put("/articles/{article_id}", response_model=Article)
def update_article(article_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        article_to_update = next((article for article in mock_articles if article["id"] == article_id), None)
        if not article_to_update:
            raise HTTPException(status_code=404, detail="Article not found")

        # Manually invoke the permission checker with owner_id
        permission_checker("update", "articles")(current_user, db, article_to_update['owner_id'])
        
        article_to_update["title"] = "Updated Title"
        return article_to_update
    finally:
        db.close()

@router.delete("/articles/{article_id}")
def delete_article(article_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        global mock_articles
        article_to_delete = next((article for article in mock_articles if article["id"] == article_id), None)
        if not article_to_delete:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Manually invoke the permission checker with owner_id
        permission_checker("delete", "articles")(current_user, db, article_to_delete['owner_id'])
        
        mock_articles = [article for article in mock_articles if article["id"] != article_id]
        return {"message": f"Article with id {article_id} deleted successfully."}
    finally:
        db.close()
