from dataclasses import dataclass


@dataclass
class Image:
    id: int
    relative_filepath: str
    width: int
    height: int
    mime: str
    classified_as: str
    unique: bool = True
    def to_dict(self):
        return {
            "id": self.id,
            "width": self.width,
            "height": self.height,
            "mime": self.mime,
            "classified_as": self.classified_as,
            "unique": self.unique
        }
    def copy_with_classified_as(self, classified_as: str):
        # Create a copy of the existing Image instance with a new `classified_as` value
        return Image(
            id=self.id,
            relative_filepath=self.relative_filepath,
            width=self.width,
            height=self.height,
            mime=self.mime,
            classified_as=classified_as,
            unique=self.unique  # Keep other fields unchanged
        )
    def copy_with_not_unique(self):
        # Create a copy of the existing Image instance with a new `classified_as` value
        return Image(
            id=self.id,
            relative_filepath=self.relative_filepath,
            width=self.width,
            height=self.height,
            mime=self.mime,
            classified_as=self.classified_as,
            unique=False  # Keep other fields unchanged
        )