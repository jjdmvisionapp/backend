from flask import Blueprint, current_app, request, jsonify, session, send_file, g
from flask_cors import cross_origin

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_data import InvalidData
from db.types.user.user_container import UserContainer
from routes.util import login_required




def create_images_blueprint(endpoint):

    images_blueprint = Blueprint('images', __name__, url_prefix=endpoint + '/images')

    @images_blueprint.route('/upload', methods=['POST'])
    @cross_origin(supports_credentials=True)
    @login_required
    def images():
        user_id = g.get("USER_ID")
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No image upload"}), 400
        image_file = request.files["IMAGE"]
        max_size = current_app.config["MAX_FILE_SIZE"]
        if image_file.mimetype not in ['image/png', 'image/jpeg'] or image_file.content_length > max_size:
            raise InvalidData("Invalid mime type")
        image_controller = DataResourceManager.get_image_data_controller(current_app)
        saved_image = image_controller.save_image(image_file, UserContainer(user_id))
        if not saved_image.unique:
            return jsonify({"status": "error", "message": "Image already exists"}), 400


    @images_blueprint.route('/get', methods=['GET'])
    @cross_origin(supports_credentials=True)
    @login_required
    def get_image():
        user_id = g.get("USER_ID")
        image_controller = DataResourceManager.get_image_data_controller(current_app)
        path, mime = image_controller.get_image_path(UserContainer(user_id))
        if path and mime is not None:
            return send_file(path, mimetype=mime)
        return jsonify({"status": "success", "message": "No image uploaded"}), 200

    return images_blueprint