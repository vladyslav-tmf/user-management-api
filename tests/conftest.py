import os
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from app.app import create_app, db
from app.models import User


@pytest.fixture(scope="session")
def app() -> Generator[Flask, None, None]:
    """Create a Flask app for testing."""
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()

    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture(scope="function")
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    """Create a test client for the app."""
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def db_session(app: Flask) -> Generator[Session, None, None]:
    """Create a clean database session for a test."""
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())

        db.session.commit()

        connection = db.engine.connect()
        transaction = connection.begin()
        session = db.session

        yield session

        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def user_data() -> dict[str, str]:
    """Return valid user data for testing."""
    return {"name": "Test User", "email": "test@example.com", "password": "Password123"}


@pytest.fixture(scope="function")
def user(db_session, user_data) -> User:
    """Create a test user in the database."""
    user = User.create(
        name=user_data["name"], email=user_data["email"], password=user_data["password"]
    )
    db.session.add(user)
    db_session.commit()

    return user


@pytest.fixture(scope="function")
def user_list(db_session) -> list[User]:
    """Create multiple test users."""
    users = []

    for i in range(3):
        user = User.create(
            name=f"User {i}", email=f"user{i}@example.com", password=f"Password{i}123"
        )
        users.append(user)
        db_session.add(user)

    db_session.commit()
    return users
