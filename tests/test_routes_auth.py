from unittest.mock import MagicMock
from src.database.models import User

user_data = {"username": "Serhio", "email": "serhio@mail.com", "password": "12345678"}


def test_signup(client, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data['user']["username"] == user_data["username"]
    assert data['user']["email"] == user_data["email"]
    assert "password" not in data['user']
    assert "avatar" in data['user']


def test_repeat_signup(client, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == 'Account already exists'


def test_not_confirmed_signin(client):
    response = client.post("api/auth/signin",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_signin(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()

    response = client.post("api/auth/signin",
                           data={"username": user.get("email"), "password": user.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_wrong_password_signin(client):
    response = client.post("api/auth/signin",
                           data={"username": user_data.get("email"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email or password"


def test_wrong_email_signin(client):
    response = client.post("api/auth/signin",
                           data={"username": "email", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email or password"


def test_validation_error_login(client):
    response = client.post("api/auth/signin",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data