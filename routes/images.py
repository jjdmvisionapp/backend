from flask import Blueprint, current_app, request, jsonify, session, send_file

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_data import InvalidData
from db.types.user.user_container import UserContainer
from routes.util import login_required

images_blueprint = Blueprint('user', __name__, url_prefix=current_app.config.get("endpoint") + '/images')

@login_required
@images_blueprint.route('/upload', methods=['POST'])
def images():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No image upload"}), 400
    image_file = request.files["IMAGE"]
    max_size = current_app.config["MAX_FILE_SIZE"]
    if image_file.mimetype not in ['image/png', 'image/jpeg'] or image_file.content_length > max_size:
        raise InvalidData
    user_id = session.get('user_id')
    image_controller = DataResourceManager.get_image_data_controller(current_app)
    saved_image = image_controller.save_image(image_file, UserContainer(user_id))
    if not saved_image.unique:
        return jsonify({"status": "error", "message": "Image already exists"}), 400

@login_required
@images_blueprint.route('/get', methods=['GET'])
def get_image():
    user_id = session.get('user_id')
    image_controller = DataResourceManager.get_image_data_controller(current_app)
    path, mime = image_controller.get_image_path(UserContainer(user_id))
    if path and mime is not None:
        return send_file(path, mimetype=mime)
    return jsonify({"status": "success", "message": "No image uploaded"}), 200