from db.db_adaptor import DBAdaptor


class DataController:
    def __init__(self, db_adaptor: DBAdaptor):
        self.db_adaptor = db_adaptor