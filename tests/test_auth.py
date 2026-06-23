def test_user_authentication_flows(client):
    payload = {"username": "qa_user", "email": "qa@test.com", "password": "secure_password_123"}
    # Verify account registration 
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    assert "token" in res.json()

    # Reject duplicates
    assert client.post("/api/auth/register", json=payload).status_code == 400