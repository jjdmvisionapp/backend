from dataclasses import dataclass


@dataclass
class Image:
    id: int
    relative_filepath: str
    width: int
    height: int
    mime: str
    unique: bool = True
    def to_dict(self):
        return {
            "id": self.id,
            "width": self.width,
            "height": self.height,
            "mime": self.mime,
        }