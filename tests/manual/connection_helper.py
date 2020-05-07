import requests
import json

URL = "http://localhost:/api/v1/"
PATH = "devices/1/"
URI = URL + PATH
HEADER = {
    "Content-Type" : "application/json",
}


def get_connections():
    r = requests.get(url = f'{URI}connections/')
    return r.status_code, r.json()['connections']


def add_connection(bandwidth=1000, corruption=0, duplication=0, delay=0, jitter=0, packet_loss=0):
    connection_config = {
        "connections":[
            {
                "bandwidth": bandwidth,
                "connection_name": "test",
                "corruption": corruption,
                "duplication": duplication,
                "delay": delay,
                "interface1": "LAN-A",
                "interface2": "LAN-B",
                "jitter": jitter,
                "packet_loss": packet_loss
            }
        ]
    }

    r = requests.put(url=URI, headers=HEADER, data=json.dumps(connection_config))
    return r


def remove_connection():
    connection_config = {
        "connections":[]
    }
    r = requests.put(url = URI, headers = HEADER, data = json.dumps(connection_config))
    return r


def get_connection_response(bandwidth=1000, corruption=0, duplication=0, delay=0, jitter=0, packet_loss=0):
    connection_config = {
        "connections":[
            {
                "bandwidth":bandwidth,
                "connection_name":"test",
                "corruption": corruption,
                "duplication": duplication,
                "delay":delay,
                "interface1":"LAN-A",
                "interface2":"LAN-B",
                "jitter":jitter,
                "packet_loss":packet_loss
            }
        ]
    }
    return connection_config