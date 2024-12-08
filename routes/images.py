from flask import Blueprint, current_app, request, jsonify, session, send_file, g
from flask_cors import cross_origin

from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_data import InvalidData
from db.types.user.user_container import UserContainer
from routes.util import login_required




from flask import Blueprint, request, jsonify, current_app, g
from flask_cors import cross_origin
from werkzeug.exceptions import BadRequest
from functools import wraps


def create_images_blueprint(endpoint):
    images_blueprint = Blueprint('images', __name__, url_prefix=endpoint + '/images')

    @images_blueprint.route('/upload', methods=['POST'])
    @cross_origin(supports_credentials=True)
    @login_required
    def images():
        user_id = g.get("USER_ID")
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No image upload"}), 400
        image_file = request.files["file"]
        max_size = current_app.config["MODULES"]["IMAGE_UPLOAD"]["MAX_FILE_SIZE"]
        
        if image_file.mimetype not in ['image/jpeg', 'image/png'] or image_file.content_length > max_size:
            return jsonify({"status": "error", "message": "Invalid mime type or file size exceeded"}), 400

        # Assuming you have a `DataResourceManager` to save the image
        image_controller = DataResourceManager.get_image_data_controller(current_app)
        saved_image = image_controller.save_image(image_file, UserContainer(user_id))
        print('saved image unique: ' + str(saved_image.unique))
        
        if not saved_image.unique:
            return jsonify({"status": "error", "message": "Image already exists"}), 400
        else:
            # since user can only upload one image im doing this
            classified_as = image_controller.classify_image(UserContainer(user_id))
            print(classified_as)
            return jsonify({"status": "success", "image": saved_image.copy_with_classified_as(classified_as).to_dict()}), 200

    @images_blueprint.route('/classify', methods=['GET'])
    @cross_origin(supports_credentials=True)
    @login_required
    def classify():
        user_id = g.get("USER_ID")
        image_controller = DataResourceManager.get_image_data_controller(current_app)


    @images_blueprint.route('/get', methods=['GET'])
    @cross_origin(supports_credentials=True)
    @login_required
    def get_image():
        user_id = g.get("USER_ID")
        image_controller = DataResourceManager.get_image_data_controller(current_app)
        path, mime = image_controller.get_image_path(UserContainer(user_id))
        if path and mime is not None:
            return send_file(path, mimetype=mime)
        return jsonify({"status": "error", "message": "No image uploaded"}), 400

    return images_blueprint