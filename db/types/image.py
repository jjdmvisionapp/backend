from dataclasses import dataclass


@dataclass
class Image(frozen=True):
    id: int
    relative_filepath: str
    width: int
    height: int