import os
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal

# Force evaluation of modules to map models cleanly to the metadata binder
from app.models.auth import User
from app.models.bookmarks import Bookmark, Tag, bookmark_tags
from app.services.auth import AuthService


def clear_database(db: Session):
    """
    Clears existing data safely without dropping tables to ensure a clean seed state.
    """
    print("[1/4] Purging existing records for a clean seed run...")
    try:
        # Delete link table entries first to prevent foreign key constraint failures
        db.execute(bookmark_tags.delete())
        db.query(Bookmark).delete()
        db.query(Tag).delete()
        db.query(User).delete()
        db.commit()
        print("[SUCCESS] Database cleared cleanly.")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to clear tables: {e}")
        raise


def create_sample_users(db: Session) -> list[User]:
    """
    Creates enterprise sample users using native secure hashing.
    """
    print("[2/4] Seeding user accounts...")
    users_data = [
        {"username": "ps_dev", "email": "ps@test.com", "password": "securepassword123"},
        {"username": "singh_ops", "email": "singh@test.com", "password": "securepassword123"},
        {"username": "test_qa", "email": "test@test.com", "password": "securepassword123"},
    ]
    
    seeded_users = []
    for u in users_data:
        db_user = User(
            username=u["username"],
            email=u["email"],
            password_hash=AuthService.hash_password(u["password"])
        )
        db.add(db_user)
        seeded_users.append(db_user)
        
    db.commit()
    for u in seeded_users:
        db.refresh(u)
    print(f"[SUCCESS] Created {len(seeded_users)} sample users.")
    return seeded_users


def create_sample_bookmarks_and_tags(db: Session, users: list[User]):
    """
    Seeds tags and contextual bookmarks assigned explicitly to split multi-tenant owners.
    """
    print("[3/4] Seeding tags and bookmarks collections...")
    
    # 1. Spin up shared master tag records
    tag_names = ["python", "api", "devops", "learning", "database"]
    tag_map = {}
    for name in tag_names:
        tag = Tag(name=name)
        db.add(tag)
        tag_map[name] = tag
    db.commit()

    # Get references to individual owners
    ps, singh, test = users[0], users[1], users[2]

    # 2. Add Bookmarks for ps (Developer Focus)
    ps_bookmarks = [
        Bookmark(
            user_id=ps.id,
            url="https://fastapi.tiangolo.com",
            title="FastAPI Official Documentation",
            description="The core framework reference docs for routing, dependencies, and path operations.",
            tags=[tag_map["python"], tag_map["api"], tag_map["learning"]]
        ),
        Bookmark(
            user_id=ps.id,
            url="https://www.sqlalchemy.org",
            title="SQLAlchemy ORM Reference",
            description="Comprehensive data mapper patterns and connection pooling logic guidelines.",
            tags=[tag_map["python"], tag_map["database"]]
        ),
        Bookmark(
            user_id=ps.id,
            url="https://docs.pytest.org",
            title="Pytest Automated Framework",
            description="Testing framework documentation optimizing unit checks, mock injection, and fixtures.",
            tags=[tag_map["python"], tag_map["learning"]]
        )
    ]

    # 3. Add Bookmarks for singh (DevOps Focus)
    singh_bookmarks = [
        Bookmark(
            user_id=singh.id,
            url="https://www.docker.com",
            title="Docker Containerization",
            description="Enterprise engine to build, package, share, and run isolated microservice apps.",
            tags=[tag_map["devops"], tag_map["learning"]]
        ),
        Bookmark(
            user_id=singh.id,
            url="https://github.com/features/actions",
            title="GitHub Actions CI/CD Pipelines",
            description="Automate software workflows right out of your version control branch repositories.",
            tags=[tag_map["devops"], tag_map["api"]]
        )
    ]

    # 4. Add Bookmarks for test (QA / Test Focus)
    test_bookmarks = [
        Bookmark(
            user_id=test.id,
            url="https://swagger.io",
            title="Swagger Interactive UI tools",
            description="API layout sandbox built on OpenAPI design specifications for direct payload contract validation.",
            tags=[tag_map["api"], tag_map["learning"]]
        )
    ]

    # Add and commit everything safely
    db.add_all(ps_bookmarks + singh_bookmarks + test_bookmarks)
    db.commit()
    print(f"[SUCCESS] Seeded {len(ps_bookmarks) + len(singh_bookmarks) + len(test_bookmarks)} granular multi-tenant bookmarks.")


def main():
    print("==========================================================")
    print("          STARTING BOOKMARKS SYSTEM DATA SEEDER           ")
    print("==========================================================")
    
    # Target live active production database structure
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        clear_database(db)
        users = create_sample_users(db)
        create_sample_bookmarks_and_tags(db, users)
        print("==========================================================")
        print(" [COMPLETE] SEED EXECUTION CONCLUDED WITHOUT ERROR ")
        print("==========================================================")
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] Seeding stopped prematurely: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()