from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.app import db
from app.models import User
from app.schemas import UserUpdateSchema, user_create_schema, user_schema, users_schema

docs_bp = Blueprint("api_docs", __name__)

api = Api(
    docs_bp,
    version="1.0",
    title="User Management API",
    description="A simple REST API for managing users",
    doc="/",
)

ns_users = api.namespace("users", description="User operations", path="/api/v1/users")

user_model = api.model(
    "User",
    {
        "id": fields.Integer(readonly=True, description="User unique identifier"),
        "name": fields.String(required=True, description="User name"),
        "email": fields.String(required=True, description="User email"),
        "created_at": fields.DateTime(
            readonly=True, description="User creation timestamp"
        ),
    },
)

user_input_model = api.model(
    "UserInput",
    {
        "name": fields.String(required=True, description="User name"),
        "email": fields.String(required=True, description="User email"),
        "password": fields.String(required=True, description="User password"),
    },
)

user_update_model = api.model(
    "UserUpdate",
    {
        "name": fields.String(required=True, description="Updated user name"),
        "email": fields.String(required=True, description="Updated user email"),
        "password": fields.String(required=True, description="Updated user password"),
    },
)

error_model = api.model(
    "Error",
    {
        "message": fields.String(required=True, description="Error message"),
        "errors": fields.Raw(description="Validation errors"),
    },
)


@ns_users.route("/")
class UserList(Resource):
    @ns_users.doc("list_users")
    @ns_users.marshal_list_with(user_model)
    def get(self) -> list:
        """List all users."""
        users = User.get_all()
        return users_schema.dump(users)

    @ns_users.doc("create_user")
    @ns_users.expect(user_input_model)
    @ns_users.response(201, "User created", user_model)
    @ns_users.response(400, "Validation error", error_model)
    @ns_users.response(409, "Email already exists", error_model)
    def post(self) -> tuple:
        """Create a new user."""
        try:
            json_data = request.get_json()

            if not json_data:
                return {"message": "No input data provided"}, 400

            user = user_create_schema.load(json_data, session=db.session)
            new_user = User.create(
                name=user.name, email=user.email, password=json_data.get("password")
            )

            db.session.add(new_user)
            db.session.commit()

            return user_schema.dump(new_user), 201

        except ValidationError as error:
            return {"message": "Validation error", "errors": error.messages}, 400
        except IntegrityError:
            db.session.rollback()
            return {"message": "User with this email already exists"}, 409
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Database error occurred"}, 500


@ns_users.route("/<int:user_id>")
@ns_users.param("user_id", "The user identifier")
@ns_users.response(404, "User not found", error_model)
class UserResource(Resource):
    @ns_users.doc("get_user")
    @ns_users.marshal_with(user_model)
    def get(self, user_id: int) -> dict:
        """Get a user by ID."""
        user = User.get_by_id(user_id)
        if not user:
            api.abort(404, f"User with id {user_id} not found")
        return user_schema.dump(user)

    @ns_users.doc("update_user")
    @ns_users.expect(user_update_model)
    @ns_users.marshal_with(user_model)
    @ns_users.response(400, "Validation error", error_model)
    def put(self, user_id: int) -> tuple:
        """Update a user."""
        try:
            json_data = request.get_json()

            if not json_data:
                return {"message": "No input data provided"}, 400

            user = User.get_by_id(user_id)

            if not user:
                return {"message": f"User with id {user_id} not found"}, 404

            required_fields = {"name", "email", "password"}

            if not all(field in json_data for field in required_fields):
                return {
                    "message": "Missing required fields",
                    "required": list(required_fields),
                }, 400

            schema = UserUpdateSchema(context={"user": user})
            updated_data = schema.load(json_data, session=db.session)

            user.name = updated_data.name
            user.email = updated_data.email
            user.password = json_data["password"]

            db.session.commit()

            return user_schema.dump(user), 200

        except ValidationError as error:
            return {"message": "Validation error", "errors": error.messages}, 400
        except IntegrityError:
            db.session.rollback()
            return {"message": "User with this email already exists"}, 409
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Database error occurred"}, 500

    @ns_users.doc("delete_user")
    @ns_users.response(204, "User deleted")
    def delete(self, user_id: int) -> tuple:
        """Delete a user."""
        try:
            user = User.get_by_id(user_id)

            if not user:
                return {"message": f"User with id {user_id} not found"}, 404

            db.session.delete(user)
            db.session.commit()

            return "", 204

        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Database error occurred"}, 500
