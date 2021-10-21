from logging import debug
from flask import Flask
from wemulate_api.api import api
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.url_map.strict_slashes = False
api.init_app(app)


def main():
    app.run(debug=True, port=80, host="0.0.0.0")


if __name__ == "__main__":
    main()
