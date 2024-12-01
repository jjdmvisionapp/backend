from abc import abstractmethod, ABC


class DBAdaptor(ABC):

    @abstractmethod
    def get_connection(self):
        pass

