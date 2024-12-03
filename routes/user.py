from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, request, current_app, jsonify, session

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_data import InvalidData
from db.types.exceptions.db_error import DBError
from routes.util import login_required

user_blueprint = Blueprint('user', __name__, url_prefix=current_app.config["endpoint"] + '/user')


@user_blueprint.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        # Safely get email and password from form
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Ensure both fields are provided
        if not email or not password:
            raise InvalidData  # Don't provide specifics for security reasons

        try:

            # Validate email using the email_validator library
            valid = validate_email(email)
            email = valid.normalized_email

            # Retrieve the user data controller to handle authentication (or other logic)
            user_controller = DataResourceManager.get_user_data_controller(current_app)

            valid_user = user_controller.validate_user(username, password, email)
            if valid_user:
                session["user_id"] = valid_user.id
                session["username"] = valid_user.username
                session["email"] = valid_user.email
                # Return a successful response (this can be a token or user info, depending on your app logic)
                return jsonify({"status": "success", "message": "Login successful"}), 200
            else:
                raise InvalidData

        except EmailNotValidError:
            # If email is invalid, raise a generic exception
            raise InvalidData  # No specific message here for security


@user_blueprint.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Ensure both fields are provided
        if not email or not password:
            raise InvalidData  # Don't provide specifics for security reasons

        user_controller = DataResourceManager.get_user_data_controller(current_app)
        user = user_controller.create_new_user(username, email, password)
        if user is not None:
            session["user_id"] = user.id
            session["username"] = user.username
            session["email"] = user.email
            return jsonify({"status": "success", "message": "Registration successful"}), 200
        else:
            raise InvalidData


@login_required
@user_blueprint.route("/update", methods=["POST"])
def update():
    if request.method == "POST":
        attribute = request.form.get("attribute")
        value = request.form.get("value")
        user_controller = DataResourceManager.get_user_data_controller(current_app)
        user_controller.update_user(session.get("user_id"), attribute, value)
        return jsonify({"status": "success", "message": "Info update successful"}), 200


@user_blueprint.route("/@me")
def get_current_user():
    user_id = session.get("user_id")  # Use .get() to safely access session keys
    if not user_id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    user = DataResourceManager.get_user_data_controller(current_app).get_user_by_id(user_id)
    if not user:
        raise DBError("Logged in user not found")
    return jsonify({"status": "success", "user": user.to_dict()}), 200


@user_blueprint.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200
