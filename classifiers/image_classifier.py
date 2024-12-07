from abc import abstractmethod, ABC
from pathlib import Path

import torch


class ImageClassifier(ABC):

    def __init__(self):
        self.model = self.load_model()  # Load the model during initialization
        self.classes = self.load_classes()  # Load classes during initialization

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

    def predict(self, image_path: Path):
        """Run prediction on the image."""
        image_tensor = self.transform_image(image_path)  # Transform the image
        with torch.no_grad():
            output = self.model(image_tensor)  # Run the model
            _, predicted = torch.max(output, 1)  # Get predicted class index
        return self.classes[predicted.item()]  # Return class label
