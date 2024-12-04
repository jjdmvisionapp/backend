from dataclasses import dataclass


@dataclass
class Image:
    id: int
    relative_filepath: str
    width: int
    height: int
    mime: str
    unique: bool = True