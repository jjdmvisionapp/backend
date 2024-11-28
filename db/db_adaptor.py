from abc import abstractmethod

class DBAdaptor:

    @abstractmethod
    def get_connection(self):
        pass

