from flask import Blueprint, current_app, request, jsonify

from routes.util import login_required

images_blueprint = Blueprint('user', __name__, url_prefix=current_app.config.get("endpoint") + '/images')

@login_required
@images_blueprint.route('/upload/<int:user_id>', methods=['POST'])
def images(user_id: int):
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No image upload"}), 400
    image_file = request.files["image"]
