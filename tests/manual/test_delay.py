import requests
import json

URL = "http://localhost:5000/api/v1/"
PATH = "hosts/1/interfaces/1/"
URI = URL + PATH

def get_interface_config():
    response = requests.get(url = URI)
    return response

def test_no_delay_before():
    r = get_interface_config()
    assert r.status_code == 200
    assert r.json() == {
        "int_id": 1,
        "host_id": 1,
        "logical_name": "lo",
        "physical_name": "lo",
        "delay": 0
    }


def test_set_delay():
    r = get_interface_config()
    assert r.status_code == 200
    assert r.json() == {
        "int_id": 1,
        "host_id": 1,
        "logical_name": "lo",
        "physical_name": "lo",
        "delay": 0
    }

    header = {
        "Content-Type" : "application/json",
    }
    data = {
        "delay": 100
    }

    r2 = requests.put(url = URI, headers = header, data = json.dumps(data))
    assert r2.status_code == 200
    assert r2.json() == {
        "int_id": 1,
        "host_id": 1,
        "logical_name": "lo",
        "physical_name": "lo",
        "delay": 100
    }

    r3 = get_interface_config()
    assert r3.status_code == 200
    assert r3.json() == {
        "int_id": 1,
        "host_id": 1,
        "logical_name": "lo",
        "physical_name": "lo",
        "delay": 100
    }


def test_remove_delay():
    r = get_interface_config()
    assert r.status_code == 200
    assert r.json() == {
        "int_id": 1,
        "host_id": 1,
        "logical_name": "lo",
        "physical_name": "lo",
        "delay": 100
    }

    header = {
        "Content-Type" : "application/json",
    }
    data = {
        "delay": 0
    }

    r2 = requests.put(url = URI, headers = header, data = json.dumps(data))
    assert r2.status_code == 200
    assert r2.json() == {
        "int_id": 1,
        "host_id": 1,
        "logical_name": "lo",
        "physical_name": "lo",
        "delay": 0
    }

    r3 = get_interface_config()
    assert r3.status_code == 200
    assert r3.json() == {
        "int_id": 1,
        "host_id": 1,
        "logical_name": "lo",
        "physical_name": "lo",
        "delay": 0
    }


#def test_delete_interface():
#    r = get_interface_config()
#    assert r.status_code == 200
#    assert r.json() == {
#        "int_id": 1,
#        "host_id": 1,
#        "logical_name": "lo",
#        "physical_name": "lo",
#        "delay": 0
#    }
#
#    r2 = requests.delete(url = URI)
#    assert r2.status_code == 204
#
#    r3 = get_interface_config()
#    assert r.status_code == 200
#    assert r.json() == {
#        "message": "Host or Interface not found"
#    }