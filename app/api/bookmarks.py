from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.dependencies import get_current_user
from app.models.auth import User
from app.models.bookmarks import Bookmark
from app.schemas.bookmarks import BookmarkCreate, BookmarkResponse, PaginatedBookmarks, StatisticsResponse
from app.services.bookmarks import BookmarkService

router = APIRouter(prefix="/api/bookmarks", tags=["Bookmarks"])


@router.get("/stats", status_code=status.HTTP_200_OK, summary="Get raw SQL bookmark statistics")
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return BookmarkService.get_raw_stats(db, user_id=current_user.id)

@router.post("", response_model=BookmarkResponse, 
            status_code=status.HTTP_201_CREATED,
            summary="Create a new bookmark entry",
            response_description="The bookmarked resource has been parsed and stored securely.")
def create_bookmark(obj_in: BookmarkCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return BookmarkService.create(db, current_user.id, obj_in)

@router.get("", 
            response_model=PaginatedBookmarks,
            status_code=status.HTTP_200_OK,
            summary="List and filter bookmarks",
            response_description="Returns a paginated payload containing matched bookmark entries.")
def list_bookmarks(
        tag: Optional[str] = Query(None),
        q: Optional[str] = Query(None),
        from_date: date = Query(None, description="Filter items created on or after this ISO date (YYYY-MM-DD)"),
        to_date: date = Query(None, description="Filter items created on or before this ISO date (YYYY-MM-DD)"),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    total, items = BookmarkService.get_filtered(
        db, current_user.id, tag, q, from_date, to_date, limit, offset
    )
    return {"total": total, "limit": limit, "offset": offset, "items": items}

@router.get("/raw_metrics",
            response_model=StatisticsResponse,
            status_code=status.HTTP_200_OK,
            summary="Retrieve user's raw metrics using raw SQL",
            response_description="Returns total counts and average metrics based on stored bookmarks.")
def get_statistics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return BookmarkService.get_metrics_raw_sql(db, current_user.id)

@router.get("/{bookmark_id}",
            response_model=BookmarkResponse,
            status_code=status.HTTP_200_OK,
            summary="Retrieve a single bookmark by ID",
            response_description="Returns the bookmark matching the provided ID, if owned by the authenticated user.")
def get_bookmark(bookmark_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark

@router.delete("/{bookmark_id}", 
                status_code=status.HTTP_204_NO_CONTENT,
                summary="Delete a bookmark by ID",
                response_description="The bookmark has been successfully deleted.")
def delete_bookmark(bookmark_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return None
