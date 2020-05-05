import requests
import json
import connection_helper

URL = "http://localhost:/api/v1/"
PATH = "devices/1/"
URI = URL + PATH
HEADER = {
    "Content-Type" : "application/json",
}


def get_parameter(parameter):
    status_code, connections = connection_helper.get_connections()
    if connections:
        print(connections)
        return connections[0][parameter]
    else:
        return -1
