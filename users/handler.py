import configparser
import hashlib
import json

import jwt
from sanic import response
from sanic.request import Request

from lib.db import Database

config = configparser.ConfigParser()
config.read("users/config.ini")
db = config["db"]


class Handler:
    """
    обработчик запросов по путям /users
    """
    salt = "fkcxs213mzxl23lasd"  # соль для ключей

    def __init__(self):
        self.db = Database(config=db)

    async def register(self, request: Request) -> response.HTTPResponse:
        """
        регистрация пользователя, POST-запрос
        :param request: запрос
        :return: json-ответ
        """
        body = await self.decode_body(request.body)
        if not body:
            return response.json(body={"error": "json decode error"}, status=400)
        username = body.get("username")
        password = body.get("password")
        email = body.get("email")
        if not username or not password or not email:
            return response.json({"error": "username, password, email required"}, status=400)

        enc_password = hashlib.md5(body.get("password") + self.salt).hexdigest()
        with self.db:
            self.db.cur.execute(
                """
                SELECT * FROM users WHERE username = '%s' OR email = '%s"
                """ % username, email
            )
            if not self.db.cur.fetchone():
                self.db.cur.execute(
                    """
                    INSERT INTO users (username, password, email)
                    VALUES ('%s', '%s', '%s')
                    """ % username, enc_password, email
                )
            else:
                return response.json({"error": "username or email busy"}, status=400)
        return response.json({"error": ""}, status=201)

    async def auth(self, request: Request) -> response.HTTPResponse:
        """
        авторизация пользователя, POST-запрос
        :param request: запрос
        :return: json-ответ
        """
        body = await self.decode_body(request.body)
        if not body:
            return response.json(body={"error": "json decode error"}, status=400)
        username = body.get("username")
        password = body.get("password")
        if not username or not password:
            return response.json({"error": "username, password required"}, status=401)

        enc_password = hashlib.md5(body.get("password") + self.salt).hexdigest()
        with self.db:
            self.db.cur.execute(
                """
                SELECT * FROM users WHERE username= '%s' AND password = '%s'
                """ % username, enc_password
            )
            user_data = self.db.cur.fetchone()
            if not user_data:
                return response.json({"error": "user not found"}, status=401)
            else:
                token = jwt.encode({"username": username, "password": enc_password}, self.salt)
                return response.json({"error": "", "token": token})

    async def get_user(self, request: Request, user_id: int) -> response.HTTPResponse:
        """
        получение данных пользователя,GET-запрос
        :param request: запрос
        :param user_id: айди пользователя в базе
        :return: json-ответ
        """
        with self.db:
            self.db.cur.execute(
                """
                SELECT username, password, email FROM users WHERE user_id = %s
                """ % user_id
            )
            user_data = self.db.cur.fetchone()
            if not user_data:
                return response.json({"error": "user not found"}, status=401)
            else:
                self.db.cur.execute(
                    """
                    SELECT title, offer_text, created FROM offers WHERE user_id = '%s' ORDER BY created
                    """ % user_id
                )
                offers = self.db.cur.fetchall()
        return response.json({"error": "", "data": user_data, "offers": offers})

    async def decode_body(self, body: Request.body) -> dict:
        """
        декодирование запроса
        :param body: тело запроса
        :return: словарь тела запроса
        """
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {}
        return body