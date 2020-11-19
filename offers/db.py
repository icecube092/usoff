


class Database:
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, "instance"):
    #         cls.instance = super(Database, cls).__new__()
    #     return cls.instance

    def __init__(self, host, port):
        self.host = host
        self.port = port