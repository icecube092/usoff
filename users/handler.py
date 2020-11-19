import json

from sanic import response
from sanic.request import Request

from .db import Database


class Handler:
    def __init__(self):
        self.db = Database()

    async def register(self, request: Request):
        body = await self.handle_errors(request.body)
        if not body:
            return response.json(body={"error": "json decode error"}, status=400)
        username = body.get("username")
        password = body.get("password")  # надо будет захэшировать
        email = body.get("email")
        with self.db:
            self.db.cur.execute(
                """
                SELECT * FROM users WHERE username = '%s' OR email = '%s"
                """ % username, password
            )
            if not self.db.cur.fetchone():
                self.db.cur.execute(
                    """
                    INSERT INTO users (username, password, email)
                    VALUES ('%s', '%s', '%s')
                    """ % username, password, email
                )
            else:
                return response.json({"error": "user already exists"}, status=400)
        return response.json({}, status=201)

    async def auth(self, request):
        pass

    async def get_user(self, request, user_id):
        print(user_id)
        return response.text("hello")

    async def handle_errors(self, body):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {}
        return body