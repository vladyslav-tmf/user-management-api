from marshmallow import ValidationError, fields, validates
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.models import User


class UserSchema(SQLAlchemyAutoSchema):
    """Schema for User model serialization and validation."""

    class Meta:
        model = User
        load_instance = True
        include_fk = True
        exclude = ("password",)

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)

    @validates("name")
    def validate_name(self, name: str) -> None:
        """Validate the name field."""
        if len(name.strip()) < 2:
            raise ValidationError("Name must be at least 2 characters long.")

        if len(name) > 255:
            raise ValidationError("Name must be at most 255 characters long.")

        if not all(char.isalnum() or char in " -'" for char in name):
            raise ValidationError(
                "Name can only contain letters, numbers, "
                "spaces, hyphens, and apostrophes."
            )


class PasswordValidationMixin:
    """Mixin for password validation logic."""

    @validates("password")
    def validate_password(self, password: str) -> None:
        """Validate the password field."""
        if not password:
            return

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        has_uppercase = any(char.isupper() for char in password)
        has_lowercase = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)

        if not has_uppercase:
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not has_lowercase:
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not has_digit:
            raise ValidationError("Password must contain at least one digit.")


class UserUpdateSchema(UserSchema, PasswordValidationMixin):
    """Schema for User model updates."""

    password = fields.String(load_only=True, required=False)

    @validates("email")
    def validate_email_unique(self, email: str) -> None:
        """Validate that the email is unique among other users."""
        if len(email) > 255:
            raise ValidationError("Email must be at most 255 characters long.")

        current_user_id = getattr(self.context.get("user"), "id", None)
        existing_user = User.get_by_email(email)

        if existing_user and existing_user.id != current_user_id:
            raise ValidationError("Email already exists.")


class UserCreateSchema(UserSchema, PasswordValidationMixin):
    """Schema for creating new users."""

    password = fields.String(load_only=True, required=True)

    @validates("email")
    def validate_email_unique(self, email: str) -> None:
        """Validate that the email is unique."""
        if len(email) > 255:
            raise ValidationError("Email must be at most 255 characters long.")

        if User.get_by_email(email):
            raise ValidationError("Email already exists.")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
