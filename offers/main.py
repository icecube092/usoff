import configparser

from sanic import Sanic
from sanic.response import text

from offers.handler import Handler


config = configparser.ConfigParser()
config.read("offers/config.ini")
server = config["server"]


app = Sanic("Test task")


@app.route("/offer/create", methods=["POST"])
async def create_offer(request):
    return text("create")


@app.route("/offer", methods=["POST"])
async def get_offer(request):
    return text("get_offer")


if __name__ == "__main__":
    handler = Handler(server["host"], int(server["port"]))
    app.run(host=server["host"], port=int(server["port"]))