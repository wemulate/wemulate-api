import requests
import json

URL = "http://localhost:/api/v1/"
PATH = "devices/"
URI = URL + PATH

def test_devices():
    r = requests.get(url = URI)
    assert r.status_code == 200
    assert r.json() == {
        "devices":[{
            "active_profile_name":"default_wemulate",
            "device_id":1,"device_name":"wemulate",
            "management_ip":"127.0.0.1"
        }]
    }

def test_get_device_1():
    r = requests.get(url = f'{URI}1/')
    assert r.status_code == 200
    assert r.json() == {
        "active_profile_name":"default_wemulate",
        "connections":[],
        "device_id":1,
        "device_name":"wemulate",
        "interfaces":[
            {
                "interface_id":1,
                "logical_name":"LAN-A",
                "physical_name":"eth1"
            },
            {
                "interface_id":2,
                "logical_name":"LAN-B",
                "physical_name":"eth2"
            }
        ],
        "management_ip":"127.0.0.1"
    }
