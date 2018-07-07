# -*- encoding: utf-8 -*-
from flask import Flask
from views.restaurant import restaurant
from views.menu_item import menu_item
from views.authentication import authentication
from views.api import api


app = Flask(__name__)

# Register all the blueprints.
app.register_blueprint(restaurant)
app.register_blueprint(menu_item)
app.register_blueprint(authentication)
app.register_blueprint(api)


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.run(host="0.0.0.0", port=8000, debug=True)
