from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, request, current_app, jsonify, session

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_user_input import InvalidUserInput
from db.types.exceptions.db_error import DBError

user_blueprint = Blueprint('user', __name__, url_prefix=current_app.config["endpoint"] + '/user')

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Safely get email and password from form
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Ensure both fields are provided
        if not email or not password:
            raise InvalidUserInput  # Don't provide specifics for security reasons

        try:
            # Validate email using the email_validator library
            valid = validate_email(email)
            email = valid.normalized_email
        except EmailNotValidError:
            # If email is invalid, raise a generic exception
            raise InvalidUserInput  # No specific message here for security

        # Retrieve the user data controller to handle authentication (or other logic)
        user_controller = DataResourceManager.get_user_data_controller(current_app)

        user = user_controller.create_new_user(username, email, password)
        session["user_id"] = user.id
        session["username"] = user.username
        session["email"] = user.email

        # Return a successful response (this can be a token or user info, depending on your app logic)
        return jsonify({"status": "success", "message": "Login successful"}), 200

