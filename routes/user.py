from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, request, current_app, jsonify, session, g

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_data import InvalidData
from db.types.exceptions.db_error import DBError
from db.types.user.user_container import UserContainer
from routes.util import login_required


def create_user_blueprint(base_endpoint):
    user_blueprint = Blueprint('user', __name__, url_prefix=base_endpoint + '/user')

    @user_blueprint.route("/login", methods=["POST"])
    def login():
        data = request.json

        # Safely get email and password from the JSON payload
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # Ensure both fields are provided
        if not email or not password:
            raise InvalidData("No email or password")

        try:
            # Validate email using the email_validator library
            valid = validate_email(email)
            email = valid.normalized

            # Retrieve the user data controller to handle authentication
            user_controller = DataResourceManager.get_user_data_controller(current_app)
            valid_user = user_controller.validate_user(username, password, email)
            if valid_user:
                session["USER_ID"] = valid_user.id
                session["USERNAME"] = valid_user.username
                session["EMAIL"] = valid_user.email
                return jsonify(
                    {"status": "success", "message": "Login successful", "session": valid_user.to_dict()}), 200
            else:
                raise InvalidData("Incorrect login")

        except EmailNotValidError:
            raise InvalidData("Invalid email")

    @user_blueprint.route("/register", methods=["POST"])
    def register():
        data = request.json

        # Safely get user details from the JSON payload
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # Ensure all fields are provided
        if not email or not password:
            raise InvalidData("No email or password")

        user_controller = DataResourceManager.get_user_data_controller(current_app)
        user = user_controller.create_new_user(username, email, password, 'user')
        if user is not None:
            session["USER_ID"] = user.id
            session["USERNAME"] = user.username
            session["EMAIL"] = user.email
            return jsonify({"status": "success", "message": "Registration successful", "user": user.to_dict()}), 200
        else:
            raise DBError("Fatal error")

    @user_blueprint.route("/update", methods=["POST"])
    @login_required
    def update():
        user_id = g.get("USER_ID")
        data = request.json

        # Update user with new attributes provided in JSON payload
        user_controller = DataResourceManager.get_user_data_controller(current_app)
        user_controller.update_user(UserContainer(user_id), data)
        return jsonify({"status": "success", "message": "Info update successful"}), 200

    @user_blueprint.route("/@me")
    @login_required
    def get_current_user():
        user_id = g.get("USER_ID")
        user = DataResourceManager.get_user_data_controller(current_app).get_user_by_id(user_id)
        return jsonify({"status": "success", "user": user.to_dict()}), 200

    @user_blueprint.route("/logout", methods=["POST", "GET"])
    @login_required
    def logout():
        session.clear()
        return jsonify({"status": "success", "message": "Logged out successfully"}), 200

    @user_blueprint.route("/delete", methods=["POST"])
    @login_required
    def delete():
        user_id = g.get("USER_ID")
        user_controller = DataResourceManager.get_user_data_controller(current_app)
        user_controller.delete_user(user_id)
        return jsonify({"status": "success", "message": "Delete successful"}), 200

    return user_blueprint
