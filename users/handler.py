import configparser
import datetime
import hashlib

from sanic import response
from sanic.request import Request

import lib.util as util
from lib.db import Database

config = configparser.ConfigParser()
config.read("users/config.ini")
db = config["db"]


class Handler:
    """
    обработчик запросов по путям /users
    """
    def __init__(self):
        self.db = Database(config=db)

    async def register(self, request: Request) -> response.HTTPResponse:
        """
        регистрация пользователя, POST-запрос
        :param request: запрос
        :return: json-ответ
        """
        body = await util.decode_body(request.body)
        if not body:
            return response.json(body={"error": "json decode error"}, status=400)
        username = body.get("username")
        password = body.get("password")
        email = body.get("email")
        if not username or not password or not email:
            return response.json({"error": "username, password, email required"}, status=400)

        enc_password = hashlib.md5(str(body.get("password") + util.salt).encode()).hexdigest()
        with self.db:
            self.db.cur.execute(
                """
                SELECT * FROM users WHERE username = '%s' OR email = '%s'
                """ % (username, email)
            )
            if not self.db.cur.fetchone():
                self.db.cur.execute(
                    """
                    INSERT INTO users (username, password, email)
                    VALUES ('%s', '%s', '%s')
                    """ % (username, enc_password, email)
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
        body = await util.decode_body(request.body)
        if not body:
            return response.json(body={"error": "json decode error"}, status=400)
        username = body.get("username")
        password = body.get("password")
        if not username or not password:
            return response.json({"error": "username, password required"}, status=401)

        enc_password = hashlib.md5(str(body.get("password") + util.salt).encode()).hexdigest()
        with self.db:
            self.db.cur.execute(
                """
                SELECT * FROM users WHERE username= '%s' AND password = '%s'
                """ % (username, enc_password)
            )
            user_data = self.db.cur.fetchone()
            if not user_data:
                return response.json({"error": "user not found"}, status=401)
            else:
                token = util.get_token(username, util.salt)
                # self.db.cur.execute(
                #     """
                #     INSERT INTO tokens (token, user_id)
                #     VALUES ('%s', '%s')
                #     ON CONFLICT (user_id) DO UPDATE
                #     SET token = '%s' WHERE user_id = '%s'
                #     """ % (token, user_data[0], token, user_data[0])
                # )
                return response.json(
                    {"error": "", "token": token}, headers={"Authorization": token}, status=201)

    async def get_user(self, request: Request, user_id: int) -> response.HTTPResponse:
        """
        получение данных пользователя, GET-запрос
        :param request: запрос
        :param user_id: айди пользователя в базе
        :return: json-ответ
        """
        token = request.headers.get("authorization")
        if not token:
            return response.json({"error": "no token"}, status=400)
        else:
            if not util.check_token(token, util.salt):
                return response.json({"error": "token expired or not exists"}, status=400)
        with self.db:
            self.db.cur.execute(
                """
                SELECT username, password, email FROM users WHERE id = %s
                """ % user_id
            )
            user_data = self.db.cur.fetchone()
            if not user_data:
                return response.json({"error": "user not found"}, status=401)
            else:
                self.db.cur.execute(
                    """
                    SELECT title, offer_text, created FROM offers WHERE user_id = '%s' 
                    ORDER BY created DESC
                    """ % user_id
                )
                offers = self.db.cur.fetchall()
                offers_to_send = []
                for offer in offers:
                    if offer:
                        offers_to_send.append([offer[0], offer[1],
                                       datetime.datetime.strftime(offer[2], "%Y-%m-%d %H:%M:%S")])
        return response.json({"error": "", "data": user_data, "offers": offers_to_send})
