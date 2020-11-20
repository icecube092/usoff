from configparser import SectionProxy

import psycopg2


class Database:
    """
    интерфейс базы данных
    """
    def __init__(self, config: SectionProxy):
        """
        :param config: секция конфига с параметрами базы
        """
        self.config = config
        conn = psycopg2.connect(dbname="postgres", user="postgres", password=self.config["password"],
                                host=self.config["host"], port=int(self.config["port"]))
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 1 FROM pg_catalog.pg_database WHERE datname = '%s'
            """ % self.config["db"]
        )
        exists = cur.fetchone()
        if not exists:
            cur.execute(
                """
                CREATE DATABASE %s
                """ % self.config["db"]
            )
        cur.close()
        conn.close()

        conn = psycopg2.connect(dbname=self.config["db"], user=self.config["user"],
                                password=self.config["password"],
                                host=self.config["host"], port=int(self.config["port"]))
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username VARCHAR(20) NOT NULL,
            password TEXT NOT NULL,
            email VARCHAR(60) NOT NULL)
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS offers(
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            offer_text TEXT NOT NULL,
            created TIMESTAMP NOT NULL,
            user_id INTEGER NOT NULL)
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tokens(
            id SERIAL PRIMARY KEY,
            token TEXT NOT NULL,
            user_id INTEGER NOT NULL)
            """
        )
        cur.close()
        conn.close()

    def __enter__(self):
        self.conn = psycopg2.connect(dbname=self.config["db"],
                                     user=self.config["user"],
                                     password=self.config["password"],
                                     host=self.config["host"])
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def __exit__(self, *args):
        self.conn.commit()
        self.cur.close()
        self.conn.close()