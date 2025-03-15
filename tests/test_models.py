import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User


def test_create_user(db_session: Session, user_data: dict[str, str]) -> None:
    """Test creating a user."""
    user = User.create(
        name=user_data["name"], email=user_data["email"], password=user_data["password"]
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
    assert user._password is not None
    assert user._password != user_data["password"]
    assert user.created_at is not None


def test_user_representation(user: User) -> None:
    """Test the string representation of a user."""
    assert repr(user) == f"<User {user.name}, email: {user.email}>"


def test_user_password_property(user: User) -> None:
    """Test the password property of a user."""
    with pytest.raises(AttributeError):
        _ = user.password


def test_user_password_setter(user: User, db_session: Session) -> None:
    """Test settings a user's password."""
    new_password = "NewPassword456"
    user.password = new_password
    db_session.commit()

    assert user._password != new_password
    assert user.check_password(new_password)
    assert not user.check_password("Password123")


def test_user_check_password(user: User) -> None:
    """Test password verification."""
    assert user.check_password("Password123")
    assert not user.check_password("WrongPassword")
    assert not user.check_password("password123")


def test_get_all_users(user_list: list[User], db_session: Session) -> None:
    """Test getting all users."""
    users = User.get_all()
    assert len(users) == len(user_list)


def test_get_user_by_id(user: User, db_session: Session) -> None:
    """Test getting a user by ID."""
    found_user = User.get_by_id(user.id)

    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.name == user.name
    assert User.get_by_id(999) is None


def test_get_user_by_email(user: User, db_session: Session) -> None:
    """Test getting a user by email."""
    found_user = User.get_by_email(user.email)

    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.email == user.email
    assert not User.get_by_email("nonexistent@examle.com")


def test_unique_email_constraint(user: User, db_session: Session) -> None:
    """Test that email must be unique."""
    duplicate_user = User.create(
        name="Another User",
        email=user.email,
        password="Password456",
    )
    db_session.add(duplicate_user)

    with pytest.raises(IntegrityError):
        db_session.commit()
