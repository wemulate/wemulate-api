import requests
import json
import connection_helper
import parameter_helper

URL = "http://localhost:/api/v1/"
PATH = "devices/1/"
URI = URL + PATH
HEADER = {
    "Content-Type" : "application/json",
}


def test_delay():
    connection_helper.remove_connection()
    r = connection_helper.add_connection(delay=50)
    assert r.status_code == 200
    assert r.json() == connection_helper.get_connection_response(delay=50)
    assert parameter_helper.get_parameter("delay") == 50


def test_jitter():
    connection_helper.remove_connection()
    r = connection_helper.add_connection(jitter=8)
    assert r.status_code == 200
    assert r.json() == connection_helper.get_connection_response(jitter=8)
    assert parameter_helper.get_parameter("jitter") == 8
    connection_helper.remove_connection()


def test_bandwidth():
    connection_helper.remove_connection()
    r = connection_helper.add_connection(bandwidth=100)
    assert r.status_code == 200
    assert r.json() == connection_helper.get_connection_response(bandwidth=100)
    assert parameter_helper.get_parameter("bandwidth") == 100
    connection_helper.remove_connection()


def test_corruption():
    connection_helper.remove_connection()
    r = connection_helper.add_connection(corruption=10)
    assert r.status_code == 200
    assert r.json() == connection_helper.get_connection_response(corruption=10)
    assert parameter_helper.get_parameter("corruption") == 10
    connection_helper.remove_connection()


def test_duplication():
    connection_helper.remove_connection()
    r = connection_helper.add_connection(duplication=11)
    assert r.status_code == 200
    assert r.json() == connection_helper.get_connection_response(duplication=11)
    assert parameter_helper.get_parameter("duplication") == 11
    connection_helper.remove_connection()


def test_packet_loss():
    connection_helper.remove_connection()
    r = connection_helper.add_connection(packet_loss=15)
    assert r.status_code == 200
    assert r.json() == connection_helper.get_connection_response(packet_loss=15)
    assert parameter_helper.get_parameter("packet_loss") == 15
    connection_helper.remove_connection()
