import pytest
from marshmallow import ValidationError
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserUpdateSchema, user_create_schema, user_schema, users_schema


def test_user_schema_serialization(user: User) -> None:
    """Test serialization of a user."""
    result = user_schema.dump(user)

    assert result["id"] == user.id
    assert result["name"] == user.name
    assert result["email"] == user.email
    assert "created_at" in result
    assert "_password" not in result


def test_users_schema_serialization(user_list: list[User]) -> None:
    """Test serialization of multiple users."""
    result = users_schema.dump(user_list)

    assert len(result) == len(user_list)

    for i, user_data in enumerate(result):
        assert user_data["id"] == user_list[i].id
        assert user_data["name"] == user_list[i].name
        assert user_data["email"] == user_list[i].email


def test_user_create_schema_validation(db_session: Session) -> None:
    """Test validation for user creation."""
    valid_data = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "Password123",
    }
    result = user_create_schema.load(valid_data, session=db_session)

    assert isinstance(result, User)
    assert result.name == valid_data["name"]
    assert result.email == valid_data["email"]

    with pytest.raises(ValidationError) as error:
        user_create_schema.load(
            {"name": "A", "email": "short@example.com", "password": "Password123"},
            session=db_session,
        )
    assert "Name must be at least 2 characters long" in str(error.value)

    with pytest.raises(ValidationError) as error:
        user_create_schema.load(
            {
                "name": "Name with $ symbol",
                "email": "invalid@example.com",
                "password": "Password123",
            },
            session=db_session,
        )
    assert "Name can only contain letters" in str(error.value)

    with pytest.raises(ValidationError) as error:
        user_create_schema.load(
            {"name": "Email User", "email": "invalid-email", "password": "Password123"},
            session=db_session,
        )
    assert "Not a valid email address" in str(error.value)

    with pytest.raises(ValidationError) as error:
        user_create_schema.load(
            {
                "name": "Password User",
                "email": "password@example.com",
                "password": "pass",
            },
            session=db_session,
        )
    assert "Password must be at least 8 characters long" in str(error.value)

    with pytest.raises(ValidationError) as error:
        user_create_schema.load(
            {
                "name": "Password User",
                "email": "password@example.com",
                "password": "password123",
            },
            session=db_session,
        )
    assert "uppercase letter" in str(error.value)

    with pytest.raises(ValidationError) as error:
        user_create_schema.load(
            {
                "name": "Password User",
                "email": "password@example.com",
                "password": "PASSWORD123",
            },
            session=db_session,
        )
    assert "lowercase letter" in str(error.value)

    with pytest.raises(ValidationError) as error:
        user_create_schema.load(
            {
                "name": "Password User",
                "email": "password@example.com",
                "password": "PasswordABC",
            },
            session=db_session,
        )
    assert "digit" in str(error.value)


def test_user_create_schema_unique_email(user: User, db_session: Session) -> None:
    """Test that email must be unique when creating users."""
    with pytest.raises(ValidationError) as error:
        user_create_schema.load(
            {
                "name": "Another User",
                "email": user.email,
                "password": "Password456",
            },
            session=db_session,
        )

    assert "Email already exists" in str(error.value)


def test_user_update_schema_validation(user: User, db_session: Session) -> None:
    """Test validation for user update."""
    schema = UserUpdateSchema(context={"user": user})
    valid_data = {
        "name": "Updated Name",
        "email": "updated@example.com",
        "password": "UpdatedPass123",
    }
    result = schema.load(valid_data, session=db_session)

    assert result.name == valid_data["name"]
    assert result.email == valid_data["email"]

    valid_data = {
        "name": "Same Email",
        "email": user.email,
        "password": "SameEmailPass123",
    }
    result = schema.load(valid_data, session=db_session)

    assert result.name == valid_data["name"]
    assert result.email == valid_data["email"]


def test_user_update_schema_email_conflict(
    user: User, user_list: list[User], db_session: Session
) -> None:
    """Test email uniqueness validation during update."""
    schema = UserUpdateSchema(context={"user": user})

    with pytest.raises(ValidationError) as error:
        schema.load(
            {
                "name": "Conflict User",
                "email": user_list[0].email,
                "password": "ConflictPass123",
            },
            session=db_session,
        )

    assert "Email already exists" in str(error.value)
