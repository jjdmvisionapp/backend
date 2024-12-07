import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from PIL import Image as PILImage
from werkzeug.datastructures import FileStorage

from classifiers.image_classifier import ImageClassifier
from db.data_controller import DataController
from db.db_adaptor import DBAdaptor
from db.sqlite.image.util import get_image_hash
from db.types.image import Image
from db.types.user.user_container import UserContainer


class ImageDataController(DataController, ABC):

    def __init__(self, db_adaptor: DBAdaptor, image_folder_path: Path, classifier: ImageClassifier):
        super().__init__(db_adaptor, image_folder_path)
        self.image_folder_path = image_folder_path
        self.image_classifier = classifier

    def init_controller(self):
        os.makedirs(self.image_folder_path, exist_ok=True)

    def _write_image(self, image: FileStorage):
        image_name = str(uuid.uuid4())
        image = PILImage.open(image.file)
        image_mime = image.get_format_mimetype()
        path = self.image_folder_path / image_name
        image.save(path)
        image_hash = get_image_hash(path)
        return image_name, image.width, image.height, image_mime, image_hash

    def save_image(self, image: FileStorage, user: UserContainer) -> Image:
        image_name, image_width, image_height, image_hash, image_mime = self._write_image(image)
        return self._save_image_to_db(image_name, image_width, image_width, image_hash, image_mime, user)

    def update_image(self, image_id: int, image: FileStorage, user: UserContainer):
        image_name, image_width, image_height, image_hash, image_mime = self._write_image(image)
        self._update_image_db(image_id, image_name, image_width, image_height, image_hash, image_mime, user)

    @abstractmethod
    def _save_image_to_db(self, image_filename, image_width, image_height, image_hash, image_mime, user: UserContainer) -> Image:
        pass

    # supports one image per user
    def classify_image(self, user: UserContainer):
        image_path, mime = self.get_image_path(user)
        return self.image_classifier.predict(image_path)

    def get_image_path(self, user: UserContainer):
        image = self._get_image_from_db(user)
        if image is not None:
            return self.image_folder_path / image.relative_filepath, image.mime
        return None

    @abstractmethod
    def _get_image_from_db(self, user: UserContainer) -> Optional[Image]:
        pass

    @abstractmethod
    def _update_image_db(self, image_id, image_filename, image_width, image_height, image_hash, image_mime, user: UserContainer) -> Optional[str]:
        pass

    @abstractmethod
    def delete_image(self, image_id: int):
        pass
