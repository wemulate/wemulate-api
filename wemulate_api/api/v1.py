from flask_restx import Resource
from flask_restx.namespace import Namespace
from flask import request
import wemulate_api.core.utils as utils

api = Namespace("v1", description="API Version 1.0")


@api.route("/device")
class Device(Resource):
    def get(self):
        return {
            "mgmt_interfaces": utils.get_mgmt_interfaces(),
            "logical_interfaces": utils.get_logical_interfaces(),
        }


@api.route("/connections")
class ConnectionList(Resource):
    def get(self):
        return {"connections": utils.get_all_connections()}

    def post(self):
        return utils.create_connection(
            request.json["connection_name"],
            request.json["first_logical_interface_id"],
            request.json["second_logical_interface_id"],
        )


@api.route("/connections/<int:connection_id>")
class Connection(Resource):
    def put(self, connection_id):
        return utils.update_connection(request.json)

    def delete(self, connection_id):
        utils.delete_connection(connection_id)
        return "Connection deleted successfully", 204
