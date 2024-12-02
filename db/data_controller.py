from abc import abstractmethod, ABC

from db.db_adaptor import DBAdaptor


class DataController(ABC):
    def __init__(self, db_adaptor: DBAdaptor):
        self.db_adaptor = db_adaptor
    @abstractmethod
    def init_controller(self):
        pass