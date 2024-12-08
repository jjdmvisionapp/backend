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


# TODO: Refactor to use temp files ideally

class ImageDataController(DataController, ABC):

    def __init__(self, db_adaptor: DBAdaptor, image_folder_path: Path, classifier: ImageClassifier):
        super().__init__(db_adaptor)
        self.image_folder_path = image_folder_path
        self.image_classifier = classifier

    def init_controller(self):
        os.makedirs(self.image_folder_path, exist_ok=True)

    def _write_image(self, sent_image: FileStorage) -> Tuple[str, int, int, str, str, Path]:
        try:
            extension = sent_image.content_type.split('/')[1]
            image_name = str(uuid.uuid4()) + "." + extension
            image = PILImage.open(sent_image.stream)
            path = self.image_folder_path / Path(image_name)
            image.save(path)
            image_hash = get_image_hash(path)
            return image_name, image.width, image.height, image_hash, sent_image.content_type, path
        except PIL.UnidentifiedImageError:
            raise InvalidData("Invalid image file")

    def save_image(self, image: FileStorage, user: UserContainer) -> Image:
        # Process the image to get metadata
        image_name, image_width, image_height, image_hash, image_mime, image_path = self._write_image(image)

        # Check if the image is unique by checking the hash in the database
        existing_image = self._get_image_from_db_by_hash(image_hash)

        if existing_image:
            # If the image is not unique (exists in the database), return the existing image object
            # easy way, dont like it
            os.remove(image_path)
            return existing_image.copy_with_not_unique()

        # Save image to the database and retrieve the saved image object
        returned_image = self._save_image_to_db(image_name, image_width, image_height, image_hash, image_mime, user)

        return returned_image

    def classify_image(self, image_id: int) -> Optional[str]:
        # Ensure you retrieve the image correctly from the database using image_id
        image = self._get_image_from_db_id(image_id)

        if image is None:
            raise ValueError(f"Image with ID {image_id} does not exist.")

        # Perform classification (assuming you have an external image classifier)
        classified_as = self.image_classifier.predict(
            self.image_folder_path / image.relative_filepath)  # This will depend on your classifier logic

        # Update the database with the classification result
        self._update_classified_as(image_id, classified_as)

        return classified_as

    def get_id_image_filepath(self, image_id: int):
        image = self._get_image_from_db_id(image_id)
        if image is not None:
            return self.image_folder_path / image.relative_filepath
        return None

    def get_current_image_filepath(self, user: UserContainer):
        image = self._get_image_from_current(user)
        if image is not None:
            return self.image_folder_path / image.relative_filepath, image.id
        return None

    def get_current_image(self, user: UserContainer) -> Optional[FileStorage]:
        return self._get_image_from_current(user)

    def get_image_from_id(self, image_id: int) -> Optional[FileStorage]:
        return self._get_image_from_db_id(image_id)

    @abstractmethod
    def _update_classified_as(self, image_id, classified_as):
        pass

    @abstractmethod
    def _get_image_from_current(self, user: UserContainer) -> Optional[Image]:
        pass

    @abstractmethod
    def _get_image_from_db_id(self, image_id: int) -> Optional[Image]:
        pass

    @abstractmethod
    def _get_image_from_db_by_hash(self, image_hash: str) -> Optional[Image]:
        """
        Helper method to check if an image with the same hash already exists in the database.
        """
        pass

    @abstractmethod
    def _save_image_to_db(self, image_filename, image_width, image_height, image_hash, image_mime,
                          user: UserContainer) -> Image:
        pass

    @abstractmethod
    def delete_image(self, image_id: int):
        pass
