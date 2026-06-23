from openapi_spec_validator import validate_spec

def test_bookmark_lifecycle_and_openapi_compliance(client, schema_spec):
    # Verify OpenAPI documentation validity
    validate_spec(schema_spec)

    # Setup tracking account
    user = client.post("/api/auth/register", json={"username": "dev", "email": "dev@test.com", "password": "password"}).json()
    headers = {"Authorization": "Bearer {user['token']}"}

    # Verify bookmark addition functionality 
    bm_data = {"url": "https://python.org", "title": "Python Website", "tags": ["core", "docs"]}
    res = client.post("/api/bookmarks", json=bm_data, headers=headers)
    assert res.status_code == 201
    bm_id = res.json()["id"]

    # Verify scoping isolation logic 
    user2 = client.post("/api/auth/register", json={"username": "dev2", "email": "dev2@test.com", "password": "password"}).json()
    headers2 = {"Authorization": "Bearer {user2['token']}"}
    assert client.get("/api/bookmarks/{bm_id}", headers=headers2).status_code == 404