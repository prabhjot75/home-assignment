from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base

# Import models to ensure tables are recognized in metadata tracking hooks
from app.models.auth import User
from app.models.bookmarks import Bookmark, Tag, bookmark_tags


def clear_database_records():
    """
    Safely purges data across all tables without deleting the actual schema tables,
    ensuring a completely fresh slate for your application database.
    """
    print("==========================================================")
    print("        STARTING BOOKMARKS DATABASE PURGE SEQUENCE         ")
    print("==========================================================")
    
    db: Session = SessionLocal()
    try:
        # 1. Clear the many-to-many junction table rows first to prevent FK constraint crashes
        print("[1/4] Deleting bookmark-to-tag relationships...")
        db.execute(bookmark_tags.delete())
        
        # 2. Clear out Bookmark rows
        print("[2/4] Purging bookmark rows...")
        deleted_bookmarks = db.query(Bookmark).delete()
        
        # 3. Clear out Tag rows
        print("[3/4] Purging tag master list records...")
        deleted_tags = db.query(Tag).delete()
        
        # 4. Clear out User accounts
        print("[4/4] Purging user accounts...")
        deleted_users = db.query(User).delete()
        
        # Commit all transaction deletions to disk atomicaly
        db.commit()
        
        print("==========================================================")
        print(" [SUCCESS] DATABASE PURGE EXECUTED WITHOUT ERROR ")
        print(f"   - Removed {deleted_users} User account profiles.")
        print(f"   - Removed {deleted_bookmarks} Bookmark catalog links.")
        print(f"   - Removed {deleted_tags} Tag catalog classifications.")
        print("==========================================================")
        
    except Exception as e:
        db.rollback()
        print(f"\n[CRITICAL FAILURE] Purge rolled back due to error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    clear_database_records()