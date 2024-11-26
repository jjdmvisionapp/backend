from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, request, current_app, jsonify, session

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_data import InvalidData

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

            user = user_controller.get_user_by_username(username)
            if user is not None:
                if user.email == email:
                    session["user_id"] = user.id
                    session["username"] = user.username
                    session["email"] = user.email
                    # Return a successful response (this can be a token or user info, depending on your app logic)
                    return jsonify({"status": "success", "message": "Login successful"}), 200
                else:
                    raise InvalidData
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
