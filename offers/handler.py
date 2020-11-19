from .db import Database


class Handler:
    def __init__(self, host, port):
        self.db = Database(host, port)