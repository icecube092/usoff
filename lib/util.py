import datetime
import json

import jwt
from sanic.request import Request


salt = "fkcxs213mzxl23lasd"


async def decode_body(body: Request.body) -> dict:
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


def get_token(username: str, salt: str) -> str:
    """
    получение jwt-токена
    :param username: имя пользователя
    :param salt: соль
    :return: токен
    """
    return jwt.encode({
        "username": username,
        "expired_at": datetime.datetime.strftime(
            datetime.datetime.now() + datetime.timedelta(minutes=10), "%Y-%m-%d %H:%M:%S")
    },
        salt
    ).decode()


def check_token(token: str, salt: str) -> bool:
    """
    проверка истечения токена
    :param token: токен
    :param salt: соль
    :return: истек или нет
    """
    try:
        dec_token = jwt.decode(token, salt)
    except jwt.exceptions.DecodeError:
        return False
    else:
        return datetime.datetime.strptime(
            dec_token["expired_at"], "%Y-%m-%d %H:%M:%S") >= datetime.datetime.now()
