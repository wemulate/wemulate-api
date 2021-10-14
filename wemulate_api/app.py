from flask import Flask
from wemulate_api.api import api

app = Flask(__name__)
app.url_map.strict_slashes = False
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
