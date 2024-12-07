from abc import abstractmethod, ABC
from pathlib import Path


class ImageClassifier(ABC):

    def __init__(self):  # Load the model during initialization
        self.classes = self.load_classes()
        self.model = self.load_model()

    @abstractmethod
    def load_model(self):
        """Load and return the model."""
        pass

    @abstractmethod
    def load_classes(self):
        """Load and return the classes."""
        pass

    @abstractmethod
    def transform_image(self, image_path: Path):
        """Apply image transformation to the input image."""
        pass
    
    @abstractmethod
    def predict(self, image_path: Path):
        pass
        
