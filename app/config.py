import os


class Config:
    """Base configuration class."""

    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"

    DB_USER: str = os.getenv("POSTGRES_USER")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    DB_HOST: str = os.getenv("POSTGRES_HOST")
    DB_PORT: str = os.getenv("POSTGRES_PORT")
    DB_NAME: str = os.getenv("POSTGRES_DB")

    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    if TESTING:
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
