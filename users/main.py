import configparser

from sanic import Sanic

from users.handler import Handler

config = configparser.ConfigParser()
config.read("users/config.ini")
server = config["server"]


app = Sanic("Users")


if __name__ == "__main__":
    handler = Handler(server["host"], int(server["port"]))

    app.add_route(handler.get_user, "/user/<user_id>", methods=["GET"])
    app.add_route(handler.auth, "/user/auth", methods=["POST"])
    app.add_route(handler.register, "/user/registry", methods=["POST"])

    app.run(host=server["host"], port=int(server["port"]))