import json

from flask import Flask, url_for
from flask.testing import FlaskClient

from app.models import User


def test_get_users(client: FlaskClient, user_list: list[User], app: Flask) -> None:
    """Test getting all users."""
    with app.app_context():
        url = url_for("users.get_users")

    response = client.get(url)
    assert response.status_code == 200

    data = json.loads(response.data)
    assert len(data) == len(user_list)


def test_get_user(client: FlaskClient, user: User, app: Flask) -> None:
    """Test getting a user by ID."""
    with app.app_context():
        url = url_for("users.get_user", user_id=user.id)

    response = client.get(url)
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["id"] == user.id
    assert data["name"] == user.name
    assert data["email"] == user.email


def test_get_nonexistent_user(client: FlaskClient, app: Flask) -> None:
    """Test getting a nonexistent user."""
    with app.app_context():
        url = url_for("users.get_user", user_id=999)

    response = client.get(url)
    assert response.status_code == 404

    data = json.loads(response.data)
    assert "message" in data
    assert "not found" in data["message"].lower()


def test_create_user(client: FlaskClient, app: Flask) -> None:
    """Test creating a user."""
    with app.app_context():
        url = url_for("users.create_user")

    new_user_data = {
        "name": "New Test User",
        "email": "newtest@example.com",
        "password": "TestPassword123",
    }

    response = client.post(
        url, data=json.dumps(new_user_data), content_type="application/json"
    )
    assert response.status_code == 201

    data = json.loads(response.data)
    assert data["name"] == new_user_data["name"]
    assert data["email"] == new_user_data["email"]
    assert "id" in data
    assert "created_at" in data

    with app.app_context():
        user = User.get_by_email(new_user_data["email"])
        assert user is not None
        assert user.name == new_user_data["name"]


def test_create_user_with_duplicate_email(
    client: FlaskClient, user: User, app: Flask
) -> None:
    """Test creating a user with an existing email."""
    with app.app_context():
        url = url_for("users.create_user")

    duplicate_user_data = {
        "name": "Duplicate User",
        "email": user.email,
        "password": "DuplicatePass123",
    }

    response = client.post(
        url, data=json.dumps(duplicate_user_data), content_type="application/json"
    )
    assert response.status_code == 400

    data = json.loads(response.data)
    assert "message" in data
    assert "error" in data
    assert "email already exists" in str(data).lower()


def test_create_user_with_invalid_data(client: FlaskClient, app: Flask) -> None:
    """Test creating a user with invalid data."""
    with app.app_context():
        url = url_for("users.create_user")

    invalid_user_data = {
        "name": "I",
        "email": "invalid_email",
        "password": "short",
    }

    response = client.post(
        url, data=json.dumps(invalid_user_data), content_type="application/json"
    )
    assert response.status_code == 400

    data = json.loads(response.data)
    assert "message" in data
    assert "validation error" in data["message"].lower()
    assert "errors" in data


def test_update_user(client: FlaskClient, user: User, app: Flask) -> None:
    """Test updating a user."""
    with app.app_context():
        url = url_for("users.update_user", user_id=user.id)

    updated_data = {
        "name": "Updated User",
        "email": "updated@example.com",
        "password": "UpdatedPass123",
    }

    response = client.put(
        url, data=json.dumps(updated_data), content_type="application/json"
    )
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["name"] == updated_data["name"]
    assert data["email"] == updated_data["email"]

    with app.app_context():
        updated_user = User.get_by_id(user.id)
        assert updated_user.name == updated_data["name"]
        assert updated_user.email == updated_data["email"]
        assert updated_user.check_password(updated_data["password"])


def test_update_nonexistent_user(client: FlaskClient, app: Flask) -> None:
    """Test updating a nonexistent user."""
    with app.app_context():
        url = url_for("users.update_user", user_id=999)

    updated_data = {
        "name": "Updated User",
        "email": "updated@example.com",
        "password": "UpdatedPass123",
    }

    response = client.put(
        url, data=json.dumps(updated_data), content_type="application/json"
    )
    assert response.status_code == 404

    data = json.loads(response.data)
    assert "message" in data
    assert "not found" in data["message"].lower()


def test_update_user_with_invalid_data(
    client: FlaskClient, user: User, app: Flask
) -> None:
    """Test updating a user with invalid data."""
    with app.app_context():
        url = url_for("users.update_user", user_id=user.id)

    invalid_data = {
        "name": "X",
        "email": user.email,
        "password": "UpdatedPass123",
    }

    response = client.put(
        url, data=json.dumps(invalid_data), content_type="application/json"
    )
    assert response.status_code == 400

    data = json.loads(response.data)
    assert "message" in data
    assert "validation error" in data["message"].lower()
    assert "errors" in data


def test_delete_user(client: FlaskClient, user: User, app: Flask) -> None:
    """Test deleting a user."""
    with app.app_context():
        url = url_for("users.delete_user", user_id=user.id)

    response = client.delete(url)
    assert response.status_code == 204
    assert response.data == b""

    with app.app_context():
        deleted_user = User.get_by_id(user.id)
        assert not deleted_user


def test_delete_nonexistent_user(client: FlaskClient, app: Flask) -> None:
    """Test deleting a nonexistent user."""
    with app.app_context():
        url = url_for("users.delete_user", user_id=999)

    response = client.delete(url)
    assert response.status_code == 404

    data = json.loads(response.data)
    assert "message" in data
    assert "not found" in data["message"].lower()
