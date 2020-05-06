import requests
import json
import connection_helper

URL = "http://localhost:/api/v1/"
PATH = "devices/1/"
URI = URL + PATH
HEADER = {
    "Content-Type" : "application/json",
}


def test_no_connections():
    status_code, connections = connection_helper.get_connections()
    assert status_code == 200
    assert connections == []


def test_add_connection():
    r = connection_helper.add_connection()
    assert r.status_code == 200
    assert r.json() == connection_helper.get_connection_response()


def test_remove_connection():
    r = connection_helper.remove_connection()
    assert r.status_code == 200
    assert r.json() == {
        "connections":[]
    }
