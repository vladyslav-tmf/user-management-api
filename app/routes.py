from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.app import db
from app.models import User
from app.schemas import (
    user_create_schema,
    user_schema,
    user_update_schema,
    users_schema,
)

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/", methods=["GET"])
def get_users():
    """Get all users."""
    users = User.get_all()
    return jsonify(users_schema.dump(users)), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    """Get a user by ID."""
    user = User.get_by_id(user_id)

    if not user:
        return jsonify({"message": f"User with id {user_id} not found"}), 404

    return jsonify(user_schema.dump(user)), 200


@users_bp.route("/", methods=["POST"])
def create_user():
    """Create a new user."""
    try:
        json_data = request.get_json()

        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        user = user_create_schema.load(json_data)
        new_user = User.create(
            name=user.name, email=user.email, password=json_data.get("password")
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify(user_schema.dump(new_user)), 201

    except ValidationError as error:
        return jsonify({"message": "Validation error", "errors": error.messages}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "User with this email already exists"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "Database error occurred"}), 500


@users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id: int):
    """Update an existing user."""
    try:
        json_data = request.get_json()

        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        user = User.get_by_id(user_id)

        if not user:
            return jsonify({"message": f"User with id {user_id} not found"}), 404

        required_fields = {"name", "email", "password"}

        if not all(field in json_data for field in required_fields):
            return (
                jsonify(
                    {
                        "message": "Missing required fields",
                        "required": list(required_fields),
                    }
                ),
                400,
            )

        context = {"user": user}
        updated_data = user_update_schema.load(json_data, context=context)

        user.name = updated_data.name
        user.email = updated_data.email
        user.password = json_data["password"]

        db.session.commit()

        return jsonify(user_schema.dump(user)), 200

    except ValidationError as error:
        return jsonify({"message": "Validation error", "errors": error.messages}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "User with this email already exists"}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "Database error occurred"}), 500


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    """Delete a user."""
    try:
        user = User.get_by_id(user_id)

        if not user:
            return jsonify({"message": f"User with id {user_id} not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return "", 204

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "Database error occurred"}), 500
