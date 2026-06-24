from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.bookmarks import Bookmark, Tag
from app.schemas.bookmarks import BookmarkCreate

class BookmarkService:
    @staticmethod
    def get_or_create_tags(db: Session, tag_names: list[str]) -> list[Tag]:
        cleaned_names = list(set([name.strip().lower() for name in tag_names if name.strip()]))
        tags = []
        for name in cleaned_names:
            tag = db.query(Tag).filter(Tag.name == name).first()
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
                db.flush()  # Generate primary key immediately
            tags.append(tag)
        return tags

    @classmethod
    def create(cls, db: Session, user_id: int, obj_in: BookmarkCreate) -> Bookmark:
        tags = cls.get_or_create_tags(db, obj_in.tags)
        bookmark = Bookmark(
            url=str(obj_in.url),
            title=obj_in.title,
            description=obj_in.description,
            user_id=user_id,
            tags=tags
        )
        db.add(bookmark)
        db.commit()
        db.refresh(bookmark)
        return bookmark

    @staticmethod
    def get_filtered(db: Session, user_id: int, tag: str = None, q: str = None, 
                     from_date: datetime = None, to_date: datetime = None, 
                     limit: int = 20, offset: int = 0):
        # Uses standard 'selectin' configuration under the hood to bypass N+1 traps
        query = db.query(Bookmark).filter(Bookmark.user_id == user_id)
        
        if tag:
            query = query.join(Bookmark.tags).filter(Tag.name == tag.lower())
        if q:
            query = query.filter(
                Bookmark.title.ilike(f"%{q}%") | Bookmark.description.ilike(f"%{q}%") 
            )
        if from_date:
            query = query.filter(Bookmark.created_at >= from_date)
        if to_date:
            query = query.filter(Bookmark.created_at <= to_date)
            
        total = query.count()
        items = query.order_by(Bookmark.created_at.desc()).offset(offset).limit(limit).all()
        return total, items

    @staticmethod
    def get_metrics_raw_sql(db: Session, user_id: int) -> dict:
        # Fulfills requirements using raw SQL aggregations
        total_bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user_id).count()
        
        total_tags_query = text("""
            SELECT COUNT(DISTINCT bt.tag_id) 
            FROM bookmark_tags bt
            JOIN bookmarks b ON b.id = bt.bookmark_id
            WHERE b.user_id = :user_id
        """)
        total_tags = db.execute(total_tags_query, {"user_id": user_id}).scalar() or 0

        top_tags_query = text("""
            SELECT t.name as name, COUNT(bt.bookmark_id) as count
            FROM tags t
            JOIN bookmark_tags bt ON t.id = bt.tag_id
            JOIN bookmarks b ON b.id = bt.bookmark_id
            WHERE b.user_id = :user_id
            GROUP BY t.name
            ORDER BY count DESC, t.name ASC
            LIMIT 5
        """)
        top_tags_res = db.execute(top_tags_query, {"user_id": user_id}).mappings().all()

        monthly_query = text("""
            SELECT strftime('%Y-%m', created_at) as month, COUNT(id) as count
            FROM bookmarks
            WHERE user_id = :user_id
            GROUP BY month
            ORDER BY month DESC
        """)
        monthly_res = db.execute(monthly_query, {"user_id": user_id}).mappings().all()

        return {
            "total_bookmarks": total_bookmarks,
            "total_tags": total_tags,
            "top_tags": [dict(row) for row in top_tags_res],
            "bookmarks_per_month": [dict(row) for row in monthly_res]
        }