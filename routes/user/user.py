from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

from app.config import Config

user_blueprint = Blueprint('user', __name__, url_prefix=Config.ENDPOINT + '/user')

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
