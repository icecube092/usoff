import configparser

import psycopg2

config = configparser.ConfigParser()
config.read("users/config.ini")
db = config["db"]

class Database:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Database, cls).__new__()
        return cls.instance

    def __init__(self):
        conn = psycopg2.connect(dbname="postgres", user="postgres", password="password", host=db["host"])
        cur = conn.cursor()
        cur.execute(
            """
            CREATE DATABASE IF NOT EXISTS %s
            """ % db["db"]
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(20) NOT NULL,
            password TEXT NOT NULL,
            email VARCHAR(60) NOT NULL)
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS offers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            offer_text TEXT NOT NULL,
            user_id INTEGER NOT NULL)
            """
        )
        conn.commit()
        conn.close()

    def __enter__(self):
        self.conn = psycopg2.connect(dbname=db["db"],
                                     user=db["user"],
                                     password=db["password"],
                                     host=db["host"])
        self.cur = self.conn.cursor()

    def __exit__(self, *args):
        self.conn.commit()
        self.cur.close()
        self.conn.close()