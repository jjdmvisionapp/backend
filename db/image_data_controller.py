from abc import ABC, abstractmethod

from db.data_controller import DataController
from db.types.image import Image


class ImageDataController(ABC, DataController):
    @abstractmethod
    def save_image_to_db(self, image_path, image_width, image_height) -> Image:
        pass
    @abstractmethod
    def get_image_from_db(self, image_path) -> Image:
        pass
    @abstractmethod
    def delete_image(self, image: Image):
        pass
    @abstractmethod
    def get_all_images(self):
        pass