import jwt
import requests


r = requests.get("http://127.0.0.1:8000/user/1", b'{"username": "as", "password": "231", "email": "sasd"}', headers={"authorization": "123"})
# r = requests.post("http://127.0.0.1:8001/offer/create", b'{"user_id": 1, "title": "hello", "text": "world"}')
print(r.content)
# enc = jwt.encode({"user": "123"}, "key")
# print(enc)
# dec = jwt.decode(enc, "key")
# print(dec)