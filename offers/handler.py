import configparser
import datetime

from sanic import response
from sanic.request import Request

import lib.util as util
from lib.db import Database

config = configparser.ConfigParser()
config.read("config.ini")
db = config["db"]


class Handler:
    """
    обработчик запросов по путям /offers
    """
    def __init__(self):
        self.db = Database(config=db)

    async def create_offer(self, request: Request) -> response.HTTPResponse:
        """
        создание объявления, POST-запрос
        :param request: запрос
        :return: json-ответ
        """
        token = request.headers.get("authorization")
        if not token:
            return response.json({"error": "no token"}, status=400)
        else:
            if not util.check_token(token, util.salt):
                return response.json({"error": "token expired or not exists"}, status=400)
        body = await util.decode_body(request.body)
        now = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
        user_id = body.get("user_id")
        title = body.get("title")
        text = body.get("text")
        if not user_id or not title or not text:
            return response.json({"error": "user_id, title, text required"}, status=400)
        with self.db:
            self.db.cur.execute(
                """
                SELECT * FROM users WHERE id = %s
                """ % user_id
            )
            if not self.db.cur.fetchone():
                return response.json({"error": "user not found"}, status=404)
            self.db.cur.execute(
                """
                INSERT INTO offers (title, offer_text, created, user_id)
                VALUES ('%s', '%s', '%s', %s)
                """ % (title, text, now, user_id)
            )
        return response.json({"error": ""}, status=201)

    async def get_offer(self, request: Request) -> response.HTTPResponse:
        """
        получение обяъвлений пользователя, POST-запрос
        :param request: запрос
        :return: json-ответ
        """
        token = request.headers.get("authorization")
        if not token:
            return response.json({"error": "no token"}, status=400)
        else:
            if not util.check_token(token, util.salt):
                return response.json({"error": "token expired or not exists"}, status=400)
        body = await util.decode_body(request.body)
        user_id = body.get("user_id")
        offer_id = body.get("offer_id")
        if offer_id:
            with self.db:
                self.db.cur.execute(
                    """
                    SELECT title, offer_text, created, user_id FROM offers WHERE id = %s
                    """ % offer_id
                )
                offer = list(self.db.cur.fetchone())
                offer[2] = datetime.datetime.strftime(offer[2], "%Y-%m-%d %H:%M:%S")
            return response.json({"error": "", "offer": offer}, status=201)
        elif user_id:
            with self.db:
                self.db.cur.execute(
                    """
                    SELECT * FROM users WHERE id = %s
                    """ % user_id
                )
                if not self.db.cur.fetchone():
                    return response.json({"error": "user not found"}, status=404)
                self.db.cur.execute(
                    """
                    SELECT title, offer_text, created, user_id FROM offers WHERE user_id = %s
                    """ % user_id
                )
                offers = list(self.db.cur.fetchall())
                offers_to_send = []
                for offer in offers:
                    offer = list(offer)
                    if offer:
                        offer[2] = datetime.datetime.strftime(offer[2], "%Y-%m-%d %H:%M:%S")
                        offers_to_send.append(offer)
            return response.json({"error": "", "offers": offers_to_send}, status=201)
        else:
            return response.json({"error": "user_id or offer id required"}, status=400)
