from typing import TYPE_CHECKING, cast

from flask import Blueprint, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

from app.config import Config

user_blueprint = Blueprint('user', __name__, url_prefix=Config.ENDPOINT + '/user')

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_controller = current_app.extensions['controller'].user_controller
        email = request.form['email']
        password = request.form['password']
        current_app.user_controller.create_new_user(email, password)

