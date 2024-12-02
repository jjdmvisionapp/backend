import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from PIL import Image as PILImage
from werkzeug.datastructures import FileStorage

from db.data_controller import DataController
from db.db_adaptor import DBAdaptor
from db.types.image import Image
from db.types.user.user_container import UserContainer


class ImageDataController(DataController, ABC):

    def __init__(self, db_adaptor: DBAdaptor, image_folder_path: Path):
        super().__init__(db_adaptor, image_folder_path)
        self.image_folder_path = image_folder_path

    def init_controller(self):
        os.makedirs(self.image_folder_path, exist_ok=True)

    def save_image(self, image_name, image_file: FileStorage, user: UserContainer):
        image = PILImage.open(image_name)
        image_file.save(self.image_folder_path / image_name)
        self._save_image_to_db(image_name, image.width, image.height, user)

    @abstractmethod
    def _save_image_to_db(self, image_filename, image_width, image_height, user: UserContainer) -> Image:
        pass

    @abstractmethod
    def get_image_from_db(self, user: UserContainer) -> Optional[Image]:
        pass

    @abstractmethod
    def delete_image(self, image_id: int):
        pass
