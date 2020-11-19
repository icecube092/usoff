import requests


r = requests.post("http://127.0.0.1:8000/user/registry", b'{"username": "as", "password": "231", "email": "sasd"}')
print(r.content)