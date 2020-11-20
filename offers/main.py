import configparser

from sanic import Sanic

from offers.handler import Handler

config = configparser.ConfigParser()
config.read("offers/config.ini")
server = config["server"]


app = Sanic("Offers")
handler = Handler()


if __name__ == "__main__":
    app.add_route(handler.create_offer, "/offer/create", methods=["POST"])
    app.add_route(handler.get_offer, "/offer", methods=["POST"])

    app.run(host=server["host"], port=int(server["port"]))