import pytest

def test_user_registration_happy_path(client):
    """Test: User can register successfully with valid credentials."""
    payload = {"username": "test_dev", "email": "dev@test.com", "password": "supersecretpassword123"}
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert data["user"]["username"] == "test_dev"

def test_registration_duplicate_email_error(client):
    """Test: System rejects registration with an already occupied email address."""
    payload = {"username": "user_a", "email": "shared@test.com", "password": "password123"}
    client.post("/api/auth/register", json=payload)
    
    payload_dup = {"username": "user_b", "email": "shared@test.com", "password": "password123"}
    response = client.post("/api/auth/register", json=payload_dup)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_user_login_happy_path(client):
    """Test: Registered user can securely obtain a JWT token."""
    payload = {"username": "login_user", "email": "login@test.com", "password": "securepassword123"}
    client.post("/api/auth/register", json=payload)
    
    # Form-encoded body mapping email parameter directly onto OAuth2 username field
    login_data = {"username": "login@test.com", "password": "securepassword123"}
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    assert "token" in response.json()

def test_user_authentication_flows(client):
    """Test: Combined flow testing sequence verification."""
    payload = {"username": "qa_user", "email": "qa@test.com", "password": "secure_password_123"}
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    assert "token" in res.json()