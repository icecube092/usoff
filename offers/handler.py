import configparser
import datetime
import json

from sanic import response
from sanic.request import Request

from lib.db import Database

config = configparser.ConfigParser()
config.read("offers/config.ini")
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
        body = await self.decode_body(request.body)
        user_id = body.get("user_id")
        title = body.get("title")
        text = body.get("text")
        if not user_id or not title or not text:
            return response.json({"error": "user_id, title, text required"}, status=400)
        with self.db:
            self.db.cur.execute(
                """
                SELECT * FROM users WHERE user_id = %s
                """ % user_id
            )
            if not self.db.cur.fetchone():
                return response.json({"error": "user not found"}, status=404)
            self.db.cur.execute(
                """
                INSERT INTO offers (title, offer_text, created, user_id)
                VALUES ('%s', '%s', '%s', %s)
                """ % title, text, datetime.datetime.now().timestamp(), user_id
            )
        return response.json({"error": ""}, status=201)

    async def get_offer(self, request: Request) -> response.HTTPResponse:
        """
        получение обяъвлений пользователя, POST-запрос
        :param request: запрос
        :return: json-ответ
        """
        body = await self.decode_body(request.body)
        user_id = body.get("user_id")
        offer_id = body.get("offer_id")
        if offer_id:
            with self.db:
                self.db.cur.execute(
                    """
                    SELECT title, offer_text, created, user_id FROM offers WHERE id = %s
                    """ % offer_id
                )
                offer = self.db.cur.fetchone()
            return response.json({"error": "", "offer": offer}, status=201)
        elif user_id:
            with self.db:
                self.db.cur.execute(
                    """
                    SELECT * FROM users WHERE user_id = %s
                    """ % user_id
                )
                if not self.db.cur.fetchone():
                    return response.json({"error": "user not found"}, status=404)
                self.db.cur.execute(
                    """
                    SELECT title, offer_text, created, user_id FROM offers WHERE user_id = %s
                    """ % user_id
                )
                offers = self.db.cur.fetchall()
            return response.json({"error": "", "offers": offers}, status=201)
        else:
            return response.json({"error": "user_id or offer id required"}, status=400)

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