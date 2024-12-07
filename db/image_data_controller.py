from typing import Optional, Tuple
import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from mimetypes import guess_type

from PIL import Image as PILImage
from PIL import ImageFile

import PIL
from werkzeug.datastructures import FileStorage

from app.exceptions.invalid_data import InvalidData
from classifiers.image_classifier import ImageClassifier
from db.data_controller import DataController
from db.db_adaptor import DBAdaptor
from db.sqlite.image.util import get_image_hash
from db.types.image import Image
from db.types.user.user_container import UserContainer


class ImageDataController(DataController, ABC):

    def __init__(self, db_adaptor: DBAdaptor, image_folder_path: Path, classifier: ImageClassifier):
        super().__init__(db_adaptor)
        self.image_folder_path = image_folder_path
        self.image_classifier = classifier

    def init_controller(self):
        os.makedirs(self.image_folder_path, exist_ok=True)

    def _write_image(self, sent_image: FileStorage) -> Tuple[str, int, int, str, str]:
        try:
            format = sent_image.content_type.split('/')[1]
            image_name = str(uuid.uuid4()) + "." + format
            print(sent_image.content_type)
            image = PILImage.open(sent_image.stream)
            path = self.image_folder_path / Path(image_name)
            print(path)
            image.save(path)
            image_hash = get_image_hash(path)
            return image_name, image.width, image.height, image_hash, sent_image.content_type
        except PIL.UnidentifiedImageError:
            raise InvalidData("Invalid image file")

        

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
        image_path, image_id = self.get_image_path(user)
        if image_path:
            classified_as = self.image_classifier.predict(image_path)
            self._update_classified_as(image_id, classified_as)
            return classified_as

    def get_image_path(self, user: UserContainer):
        image = self._get_image_from_db(user)
        if image is not None:
            return self.image_folder_path / image.relative_filepath, image.id
        return None
    
    @abstractmethod
    def _update_classified_as(self, image_id, classified_as):
        pass

    @abstractmethod
    def _get_image_from_db(self, user: UserContainer) -> Optional[Image]:
        pass

    @abstractmethod
    def _update_image_db(self, image_id, image_filename, image_width, image_height, image_hash, image_mime, user: UserContainer) -> Optional[str]:
        pass

    @abstractmethod
    def delete_image(self, image_id: int):
        pass
