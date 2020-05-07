import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{path}/../../project')

import mock
import pytest
from pytest_mock import mocker
from types import SimpleNamespace
from unittest.mock import call

from core import service
from apis import salt_api
from core.database import db, utils

@pytest.fixture(autouse=True)
def setup_mocks(mocker):
    mocker.patch.object(salt_api, 'get_interfaces')
    mocker.patch.object(salt_api, 'get_management_ip')
    mocker.patch.object(salt_api, 'add_connection')
    mocker.patch.object(salt_api, 'remove_connection')
    mocker.patch.object(salt_api, 'update_connection')
    mocker.patch.object(salt_api, 'set_parameters')
    mocker.patch.object(salt_api, 'remove_parameters')
    mocker.patch.object(salt_api, 'update_parameters')
    salt_api.get_interfaces.return_value = {'return': [{'test device name': ['eth1', 'eth2', 'eth3', 'eth4']}]}
    salt_api.get_management_ip.return_value = {'return': [{'test device name': '192.168.0.1'}]}

    mocker.patch.object(utils, 'get_device')
    mocker.patch.object(utils, 'is_device_present')
    mocker.patch.object(utils, 'get_device_list')
    mocker.patch.object(utils, 'get_active_profile')
    mocker.patch.object(utils, 'get_all_interfaces')
    mocker.patch.object(utils, 'get_logical_interface')
    mocker.patch.object(utils, 'get_logical_interface_by_name')
    mocker.patch.object(utils, 'get_logical_interface_list')
    mocker.patch.object(utils, 'create_profile')
    mocker.patch.object(utils, 'create_device')
    mocker.patch.object(utils, 'create_connection')
    mocker.patch.object(utils, 'create_interface')
    mocker.patch.object(utils, 'update_parameter')
    mocker.patch.object(utils, 'update_connection')
    mocker.patch.object(utils, 'delete_connection')
    utils.get_device.return_value = SimpleNamespace(device_id=8,
                                                    device_name='test device name',
                                                    active_profile=9,
                                                    management_ip='192.168.0.1',
                                                    interfaces=[
                                                        SimpleNamespace(physical_name='eth1', device_id=8,
                                                                        logical_interface_id=1),
                                                        SimpleNamespace(physical_name='eth2', device_id=8,
                                                                        logical_interface_id=2),
                                                        SimpleNamespace(physical_name='eth3', device_id=8,
                                                                        logical_interface_id=3),
                                                        SimpleNamespace(physical_name='eth4', device_id=8,
                                                                        logical_interface_id=4)
                                                    ],
                                                    connections=[
                                                        SimpleNamespace(connection_name='connection 1',
                                                                        logical_interface1=4,
                                                                        logical_interface2=2,
                                                                        active_device_profile=9)
                                                    ])
    utils.is_device_present.return_value = False
    utils.get_device_list.return_value = [
        SimpleNamespace(),
    ]
    utils.get_active_profile.return_value = SimpleNamespace(profile_id=8,
                                                            profile_name='profile 8 name',
                                                            connections=[
                                                                SimpleNamespace(connection_name='connection 1',
                                                                                logical_interface1=4,
                                                                                logical_interface2=2,
                                                                                active_device_profile=9)
                                                            ])
    utils.get_all_interfaces.return_value = [
        SimpleNamespace(physical_name='eth1', device_id=8, logical_interface_id=1),
        SimpleNamespace(physical_name='eth2', device_id=8, logical_interface_id=2),
        SimpleNamespace(physical_name='eth3', device_id=8, logical_interface_id=3),
        SimpleNamespace(physical_name='eth4', device_id=8, logical_interface_id=4)
    ]
    utils.get_logical_interface.side_effect = [
        SimpleNamespace(logical_interface_id=1),
        SimpleNamespace(logical_interface_id=2),
        SimpleNamespace(logical_interface_id=3),
        SimpleNamespace(logical_interface_id=4)
    ]
    utils.create_profile.return_value = SimpleNamespace(profile_id=9)
    utils.create_device.return_value = SimpleNamespace(device_id=8)
    utils.create_connection.return_value = SimpleNamespace(connection_id=1)
    utils.create_interface.return_value = {}
    utils.update_connection.return_value = True
    utils.update_parameter.return_value = True

    mocker.patch.object(db.session, 'rollback')
    mocker.patch.object(db.session, 'commit')


def test_create_device(mocker):
    service.create_device('test device name')

    salt_api.get_interfaces.assert_called_with('test device name')
    salt_api.get_management_ip.assert_called_with('test device name')

    utils.is_device_present.assert_called_with('test device name')
    utils.create_profile.assert_called_with('test device name')
    utils.create_device.assert_called_with('test device name', 9, '192.168.0.1')
    utils.get_logical_interface.assert_has_calls([call(1), call(2), call(3), call(4)])
    utils.create_interface.assert_has_calls([
                                            call('eth1', 8, 1),
                                            call('eth2', 8, 2),
                                            call('eth3', 8, 3),
                                            call('eth4', 8, 4)
                                            ])

    db.session.commit.assert_called_once()
    db.session.rollback.assert_not_called()

def test_create_duplicate_device(mocker):
    service.create_device('test device name')
    utils.is_device_present.return_value = True

    try:
        service.create_device('test device name')
        assert False
    except Exception as e:
        e.args[0] == 400
        e.args[1] == "Device test device name is already registered!"
        db.session.commit.assert_called_once()
        db.session.rollback.assert_not_called()

# need to mock serialize for this to work
# def test_get_device_list(mocker):
#     device_list = service.get_device_list()
#     assert device_list == [
#         {
#             'device_id': 8,
#             'device_name': 'test device name',
#             'management_ip': '192.168.0.1',
#             'active_profile_name': 'profile 8 name'
#         }
#     ]

def test_get_device_list_empty(mocker):
    utils.get_device_list.return_value = []

    device_list = service.get_device_list()

    assert device_list == []

def test_get_device_inexistent(mocker):
    utils.get_device.side_effect=Exception(404, "Device with id 4 not found")
    try:
        service.get_device(4)
        assert False
    except Exception as e:
        assert e.args[0] == 404
        assert e.args[1] == "Device with id 4 not found"
