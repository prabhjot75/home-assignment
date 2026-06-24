# This automatically launches your browser

import uvicorn
from app.database import Base, engine
from app.models.auth import User
from app.models.bookmarks import Bookmark, Tag, bookmark_tags

def init_db():
    """
    Synchronously initializes and provisions the SQLite schema tables.
    """
    print("[INFO] Initializing SQLite database schemas...")
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] Database tables provisioned successfully.")

def main():
    init_db()
    print("[INFO] Booting up Uvicorn ASGI production server engine...")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=9500,
        reload=True  # Enables hot-reloading for development
    )

if __name__ == "__main__":  
    main()