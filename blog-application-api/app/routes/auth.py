from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.schemas.validators import (
    validate_registration_payload,
    validate_login_payload,
)
from app.utils.helpers import error_response, success_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user account with username, email, and password."""
    data = request.get_json(silent=True) or {}
    is_valid, err_msg = validate_registration_payload(data)
    if not is_valid:
        return error_response(err_msg, 400)

    username = str(data["username"]).strip()
    email = str(data["email"]).strip()
    password = str(data["password"])

    if User.find_by_username(username):
        return error_response("Username already exists.", 409)

    if User.find_by_email(email):
        return error_response("Email already exists.", 409)

    user_doc = User.create(username=username, email=email, raw_password=password)
    user_id = str(user_doc["_id"])
    access_token = create_access_token(identity=user_id)

    return success_response(
        data={"user": User.to_dict(user_doc), "access_token": access_token},
        message="User registered successfully.",
        status_code=201,
    )


@auth_bp.route("/login", methods=["POST"])
@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate existing user and return JWT access token."""
    data = request.get_json(silent=True) or {}
    is_valid, err_msg = validate_login_payload(data)
    if not is_valid:
        return error_response(err_msg, 400)

    email = str(data["email"]).strip()
    password = str(data["password"])

    user_doc = User.find_by_email(email)
    if not user_doc or not User.check_password(user_doc, password):
        return error_response("Invalid email or password.", 401)

    user_id = str(user_doc["_id"])
    access_token = create_access_token(identity=user_id)

    return success_response(
        data={"user": User.to_dict(user_doc), "access_token": access_token},
        message="Login successful.",
        status_code=200,
    )


@auth_bp.route("/me", methods=["GET"])
@auth_bp.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Retrieve profile of the currently authenticated user."""
    user_id = get_jwt_identity()
    user_doc = User.find_by_id(user_id)
    if not user_doc:
        return error_response("User not found.", 404)

    return success_response(data={"user": User.to_dict(user_doc)}, status_code=200)
