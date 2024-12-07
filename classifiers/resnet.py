# Define a class for image classification using ResNet
from pathlib import Path

from PIL import Image
from torchvision import models, transforms

from classifiers.image_classifier import ImageClassifier


class ResNetClassifier(ImageClassifier):

    def __init__(self, class_file='imagenet_classes.txt'):
        super().__init__()
        self.class_file = class_file

    def load_model(self):
        """Load the pre-trained ResNet model."""
        model = models.resnet152(pretrained=True)
        model.eval()  # Set the model to evaluation mode
        return model

    def load_classes(self):
        """Load ImageNet classes from the specified class file."""
        with open(self.class_file) as f:
            classes = [line.strip() for line in f.readlines()]
        return classes

    def transform_image(self, image_path: Path):
        """Transform the input image to match the model's input requirements."""
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        # Open and transform the image
        image = Image.open(image_path).convert('RGB')
        return transform(image).unsqueeze(0)
