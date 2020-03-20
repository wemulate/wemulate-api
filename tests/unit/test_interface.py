#from interfaces.interfaces import *

#def test_get_interface(client):
#    response = client.get('/api/v1/{host_id}/interfaces/1')
#    assert response.status_code == 200
#    assert response.json == {
#        "id": 1,
#        "name": "LAN1"
#    }

def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4
