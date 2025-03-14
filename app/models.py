from datetime import UTC, datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.app import bcrypt, db


class User(db.Model):
    """User model for storing user data."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), nullable=False
    )

    def __repr__(self) -> str:
        """Return string representation of the user."""
        return f"<User {self.name}, email: {self.email}>"

    def set_password(self, password: str) -> None:
        """Hash and set the user password."""
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password, password)

    @classmethod
    def get_all(cls) -> list["User"]:
        """Get all users."""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, user_id: int) -> "User | None":
        """Get user by ID."""
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email: str) -> "User | None":
        """Get user by email."""
        return cls.query.filter_by(email=email).first()
