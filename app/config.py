class Config:
    """Base configuration class."""

    SQLALCHEMY_DATABASE_URI: str = "sqlite:///users.db"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
