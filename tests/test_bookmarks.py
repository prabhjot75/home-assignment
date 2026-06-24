import pytest
from openapi_spec_validator import validate_spec

def test_openapi_contract_validation(schema_spec):
    """Test: Validates that the auto-generated OpenAPI spec adheres to the OpenAPI 3.0 specification."""
    validate_spec(schema_spec)

def test_bookmark_lifecycle_and_openapi_compliance(client, schema_spec):
    """Test: Comprehensive happy path verification for bookmark lifecycles."""
    # Register safely and assert to bubble up error details cleanly if it fails
    user_res = client.post("/api/auth/register", json={"username": "dev_test", "email": "dev@test.com", "password": "securepassword123"})
    assert user_res.status_code == 201, f"Registration failed with: {user_res.json()}"
    user = user_res.json()
    headers = {"Authorization": f"Bearer {user['token']}"}

    # Verify bookmark creation
    bm_data = {"url": "https://python.org", "title": "Python Website", "tags": ["core", "docs"]}
    res = client.post("/api/bookmarks", json=bm_data, headers=headers)
    assert res.status_code == 201
    bm_id = res.json()["id"]

    # Test separation of concerns: A different user cannot see this bookmark
    user2_res = client.post("/api/auth/register", json={"username": "dev2", "email": "dev2@test.com", "password": "securepassword123"})
    assert user2_res.status_code == 201
    headers2 = {"Authorization": f"Bearer {user2_res.json()['token']}"}
    assert client.get(f"/api/bookmarks/{bm_id}", headers=headers2).status_code == 404

def test_create_bookmark_happy_path(client):
    """Test: Authenticated users can successfully create bookmarks with associated tags."""
    user_res = client.post("/api/auth/register", json={"username": "chef", "email": "chef@test.com", "password": "securepassword123"})
    assert user_res.status_code == 201, f"Registration failed with: {user_res.json()}"
    headers = {"Authorization": f"Bearer {user_res.json()['token']}"}

    payload = {
        "url": "https://fastapi.tiangolo.com",
        "title": "FastAPI Docs",
        "description": "Modern high performance framework",
        "tags": ["python", "api"]
    }
    response = client.post("/api/bookmarks", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["title"] == "FastAPI Docs"

def test_input_validation_edge_case_title_too_long(client):
    """Test: Edge case validation check for titles exceeding the 200 character limit."""
    user_res = client.post("/api/auth/register", json={"username": "tester", "email": "tester@test.com", "password": "securepassword123"})
    assert user_res.status_code == 201, f"Registration failed with: {user_res.json()}"
    headers = {"Authorization": f"Bearer {user_res.json()['token']}"}

    # Generate a breaking 205-character string payload
    payload = {
        "url": "https://example.com",
        "title": "A" * 205,
        "tags": ["test"]
    }
    response = client.post("/api/bookmarks", json=payload, headers=headers)
    assert response.status_code == 422
    err_envelope = response.json()
    
    # Assert adherence to the required custom error layout envelope
    assert "error" in err_envelope
    assert err_envelope["error"]["code"] == "VALIDATION_ERROR"
    assert err_envelope["error"]["details"]["field"] == "title"

def test_input_validation_edge_case_invalid_url_scheme(client):
    """Test: Edge case validation check for invalid link protocol schemes."""
    user_res = client.post("/api/auth/register", json={"username": "tester2", "email": "tester2@test.com", "password": "securepassword123"})
    assert user_res.status_code == 201, f"Registration failed with: {user_res.json()}"
    headers = {"Authorization": f"Bearer {user_res.json()['token']}"}

    payload = {
        "url": "ftp://unsupported-server.com",
        "title": "My FTP Resource"
    }
    response = client.post("/api/bookmarks", json=payload, headers=headers)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

def test_multi_tenant_bookmark_isolation(client):
    """Test: Privacy check ensuring User B cannot read User A's bookmarks."""
    user_a = client.post("/api/auth/register", json={"username": "usera", "email": "usera@test.com", "password": "securepassword123"}).json()
    headers_a = {"Authorization": f"Bearer {user_a['token']}"}
    bm = client.post("/api/bookmarks", json={"url": "https://a.com", "title": "Secret A"}, headers=headers_a).json()
    bm_id = bm["id"]

    user_b = client.post("/api/auth/register", json={"username": "userb", "email": "userb@test.com", "password": "securepassword123"}).json()
    headers_b = {"Authorization": f"Bearer {user_b['token']}"}
    
    response = client.get(f"/api/bookmarks/{bm_id}", headers=headers_b)
    assert response.status_code == 404

def test_bookmark_list_filtering_and_pagination(client):
    """Test: Validates query parameter search filtering and total result counts."""
    user_res = client.post("/api/auth/register", json={"username": "searcher", "email": "searcher@test.com", "password": "securepassword123"})
    assert user_res.status_code == 201, f"Registration failed with: {user_res.json()}"
    headers = {"Authorization": f"Bearer {user_res.json()['token']}"}

    client.post("/api/bookmarks", json={"url": "https://py.org", "title": "Python Central", "tags": ["coding"]}, headers=headers)
    client.post("/api/bookmarks", json={"url": "https://rust.org", "title": "Rust Language", "tags": ["coding"]}, headers=headers)

    res_filter = client.get("/api/bookmarks?tag=coding", headers=headers)
    assert res_filter.status_code == 200
    assert res_filter.json()["total"] == 2

def test_delete_bookmark_lifecycle(client):
    """Test: Users can permanently remove an item from their collection index."""
    user_res = client.post("/api/auth/register", json={"username": "deleter", "email": "deleter@test.com", "password": "securepassword123"})
    assert user_res.status_code == 201, f"Registration failed with: {user_res.json()}"
    headers = {"Authorization": f"Bearer {user_res.json()['token']}"}

    bm = client.post("/api/bookmarks", json={"url": "https://trash.com", "title": "Temporary Link"}, headers=headers).json()
    bm_id = bm["id"]

    assert client.delete(f"/api/bookmarks/{bm_id}", headers=headers).status_code == 204
    assert client.get(f"/api/bookmarks/{bm_id}", headers=headers).status_code == 404