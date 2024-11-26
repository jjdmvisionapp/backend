from abc import abstractmethod

class DBAdapter:

    def __init__(self, user_table_name, chat_table_name):
        self.user_table_name = user_table_name
        self.chat_table_name = chat_table_name

    @abstractmethod
    def get_connection(self):
        pass