from flask_restx import Resource
from flask_restx.namespace import Namespace

api = Namespace("v1", description="API Version 1.0")


@api.route("/connection")
class Connection(Resource):
    def get(self):
        return {"connection": "is ready"}
