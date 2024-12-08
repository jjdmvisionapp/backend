from flask import Blueprint, current_app, request, jsonify, session, send_file, g
from flask_cors import cross_origin
from app.data_resource_manager import DataResourceManager
from app.exceptions.invalid_data import InvalidData
from db.types.user.user_container import UserContainer
from routes.util import login_required

# chatgpt helped
def create_images_blueprint(endpoint):
    images_blueprint = Blueprint('images', __name__, url_prefix=endpoint + '/images')

    @images_blueprint.route('/upload', methods=['POST'])
    @cross_origin(supports_credentials=True)
    @login_required
    def upload_image():
        user_id = g.get("USER_ID")

        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No image upload"}), 400

        image_file = request.files["file"]
        max_size = current_app.config["MODULES"]["IMAGE_UPLOAD"]["MAX_FILE_SIZE"]

        # Check file type and size
        if image_file.mimetype not in ['image/jpeg', 'image/png'] or image_file.content_length > max_size:
            return jsonify({"status": "error", "message": "Invalid mime type or file size exceeded"}), 400

        # Assuming DataResourceManager saves the image
        image_controller = DataResourceManager.get_image_data_controller(current_app)
        saved_image = image_controller.save_image(image_file, UserContainer(user_id))
        print(f'Saved image unique: {saved_image.unique}')

        # Classify the image if it's new
        if saved_image.unique:
            classified_as = image_controller.classify_image(saved_image.id)
            print(f'Image classified as: {classified_as}')

            return jsonify({
                "status": "success",
                "image": saved_image.copy_with_classified_as(classified_as).to_dict()
            }), 200
        else:
            return jsonify({"status": "success", "image": saved_image.to_dict()}), 200

    @images_blueprint.route('/get-info', methods=['GET', 'POST'])
    @cross_origin(supports_credentials=True)
    @login_required
    def get_image_info():
        user_id = g.get("USER_ID")

        if request.method == 'GET':
            # If the request is GET, get the most recent image for the user
            image_controller = DataResourceManager.get_image_data_controller(current_app)
            image = image_controller.get_current_image(UserContainer(user_id))

            if image:
                return jsonify({"status": "success", "image": image.to_dict()}), 200
            else:
                return jsonify({"status": "error", "message": "No image found for the user"}), 404

        elif request.method == 'POST':
            # If the request is POST, get the image based on image_id
            image_id = request.json.get("image_id")

            if not image_id:
                return jsonify({"status": "error", "message": "Image ID is required"}), 400

            image_controller = DataResourceManager.get_image_data_controller(current_app)
            image = image_controller.get_image_from_id(image_id)

            if image:
                return jsonify({"status": "success", "image": image.to_dict()}), 200
            else:
                return jsonify({"status": "error", "message": "Image not found"}), 404

    @images_blueprint.route('/get-file', methods=['POST'])
    @cross_origin(supports_credentials=True)
    @login_required
    def get_image_file():
        user_id = g.get("USER_ID")
        image_controller = DataResourceManager.get_image_data_controller(current_app)
        image_id = request.json.get("image_id")

        if not image_id:
            return jsonify({"status": "error", "message": "Image ID is required"}), 400

        # Fetch image file from DB
        path = image_controller.get_id_image_filepath(image_id)

        if path:
            return send_file(path)
        return jsonify({"status": "error", "message": "Can't find image requested"}), 400

    return images_blueprint
