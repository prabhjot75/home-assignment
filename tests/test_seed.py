import pytest
from app.models.auth import User
from app.models.bookmarks import Bookmark, Tag
from seed import clear_database, create_sample_users, create_sample_bookmarks_and_tags

def test_seeded_data_integrity_and_relations(db_session):
    """
    Test: Runs the exact pipeline from seed.py inside the testing sandbox
    and verifies records, hashing states, and multi-tenant tag counts.
    """
    # 1. Execute the seeding pipeline blocks using the test database session
    clear_database(db_session)
    users = create_sample_users(db_session)
    create_sample_bookmarks_and_tags(db_session, users)

    # 2. Assert Users verification
    assert len(users) == 3, "Seed script should create exactly 3 users."
    
    ps = db_session.query(User).filter(User.email == "ps@test.com").first()
    singh = db_session.query(User).filter(User.email == "singh@test.com").first()
    test = db_session.query(User).filter(User.email == "test@test.com").first()

    assert ps is not None, "ps should exist in the seeded database."
    assert singh is not None, "singh should exist in the seeded database."
    assert test is not None, "test should exist in the seeded database."

    # Verify that passwords are safely hashed and not plain-text inside the DB
    assert ps.password_hash != "securepassword123", "Passwords must be securely stored as hashes."
    assert ps.password_hash.startswith("$2b$") or len(ps.password_hash) > 20, "Password should follow a strong bcrypt/hash signature."

    # 3. Assert Bookmarks multi-tenant isolation counts
    ps_bookmarks = db_session.query(Bookmark).filter(Bookmark.user_id == ps.id).all()
    singh_bookmarks = db_session.query(Bookmark).filter(Bookmark.user_id == singh.id).all()
    test_bookmarks = db_session.query(Bookmark).filter(Bookmark.user_id == test.id).all()

    assert len(ps_bookmarks) == 3, "ps should have exactly 3 seeded bookmarks."
    assert len(singh_bookmarks) == 2, "singh should have exactly 2 seeded bookmarks."
    assert len(test_bookmarks) == 1, "test should have exactly 1 seeded bookmark."

    # 4. Assert Tag relation accuracy (Deep link verification)
    fastapi_bookmark = db_session.query(Bookmark).filter(
        Bookmark.user_id == ps.id, 
        Bookmark.title == "FastAPI Official Documentation"
    ).first()

    assert fastapi_bookmark is not None, "ps's FastAPI bookmark should exist."
    
    # Extract tag names linked to this specific bookmark record
    linked_tags = [tag.name for tag in fastapi_bookmark.tags]
    assert "python" in linked_tags, "FastAPI bookmark should be tagged with 'python'."
    assert "api" in linked_tags, "FastAPI bookmark should be tagged with 'api'."
    assert "learning" in linked_tags, "FastAPI bookmark should be tagged with 'learning'."
    assert "devops" not in linked_tags, "ps's FastAPI bookmark should not contain singh's 'devops' tag."

    # 5. Global Tag Registry Evaluation
    total_tags = db_session.query(Tag).count()
    assert total_tags == 5, "There should be exactly 5 distinct tag definitions inside the master list register."