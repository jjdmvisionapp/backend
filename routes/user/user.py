from typing import TYPE_CHECKING, cast

from flask import Blueprint, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

from app.config import Config
from app.data_resource_manager import DataResourceManager

user_blueprint = Blueprint('user', __name__, url_prefix=Config.ENDPOINT + '/user')

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_controller = DataResourceManager.get_user_data_controller(current_app)
        email = request.form['email']
        password = request.form['password']

