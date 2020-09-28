import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{path}/../../project')

import mock
import pytest
from pytest_mock import mocker
from mockup.object_mockup import ConnectionMockup, DeviceMockup, InterfaceMockup
from types import SimpleNamespace
from unittest.mock import call

from core import service
from apis import salt_api
from core.database import db, utils
from exception import WemulateException

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

    mocker.patch.object(utils, 'get_all_device_info')
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
    mocker.patch.object(utils, 'create_parameter')
    mocker.patch.object(utils, 'update_parameter')
    mocker.patch.object(utils, 'update_connection')
    mocker.patch.object(utils, 'delete_connection')
    logical_interfaces = [SimpleNamespace(logical_interface_id=i,
                                          logical_name='LAN-' + chr(ord('@') + i)) for i in range(1, 10)]
    interfaces = [InterfaceMockup(interface_id=i + 1,
                                  physical_name=f'eth{i}',
                                  device_id=8,
                                  has_logical_interface=logical_interfaces[i],
                                  logical_name=logical_interfaces[i].logical_name
                                  )
                  for i in range(4)]
    connection = ConnectionMockup(
        connection_name='connection 1',
        interface1=logical_interfaces[3].logical_name,
        interface2=logical_interfaces[1].logical_name,
        first_logical_interface=logical_interfaces[3],
        second_logical_interface=logical_interfaces[1],
        active_device_profile=9
    )
    profile = SimpleNamespace(profile_id=8,
                              profile_name='profile 8 name',
                              connections=[
                                  connection
                              ])
    device = DeviceMockup(device_id=8,
                          device_name='test device name',
                          active_profile=9,
                          active_profile_name=profile.profile_name,
                          management_ip='192.168.0.1',
                          interfaces=interfaces,
                          connections=[
                              connection
                          ])
    utils.get_all_device_info.return_value = device
    utils.is_device_present.return_value = False
    utils.get_device_list.return_value = [
        device
    ]
    utils.get_active_profile.return_value = profile
    utils.get_all_interfaces.return_value = interfaces
    utils.get_logical_interface.side_effect = logical_interfaces
    utils.get_logical_interface_by_name.side_effect = logical_interfaces
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
        assert False  # should not be reached
    except WemulateException as e:
        e.args[0] == 400
        e.args[1] == "Device test device name is already registered!"
        db.session.commit.assert_called_once()
        db.session.rollback.assert_not_called()

def test_get_device_list(mocker):
    device_list = service.get_device_list()
    assert device_list == [
        {
            'device_id': 8,
            'device_name': 'test device name',
            'management_ip': '192.168.0.1',
            'active_profile_name': 'profile 8 name'
        }
    ]

def test_get_device_list_empty(mocker):
    utils.get_device_list.return_value = []

    device_list = service.get_device_list()

    assert device_list == []

def test_get_device_inexistent(mocker):
    utils.get_all_device_info.side_effect=WemulateException(404, "Device with id 4 not found")
    try:
        service.get_all_device_info(4)
        assert False  # should not be reached
    except WemulateException as e:
        assert e.args[0] == 404
        assert e.args[1] == "Device with id 4 not found"

def test_get_interface_list(mocker):
    interface_list = service.get_interface_list(8)

    assert interface_list == [
        {
            'interface_id': 1,
            'logical_name': 'LAN-A',
            'physical_name': 'eth0'
        },
        {
            'interface_id': 2,
            'logical_name': 'LAN-B',
            'physical_name': 'eth1'
        },
        {
            'interface_id': 3,
            'logical_name': 'LAN-C',
            'physical_name': 'eth2'
        },
        {
            'interface_id': 4,
            'logical_name': 'LAN-D',
            'physical_name': 'eth3'
        },
    ]

def test_get_interface_list_empty(mocker):
    utils.get_all_interfaces.return_value = []

    interface_list = service.get_interface_list(8)

    assert interface_list == []

def test_get_connection_list(mocker):
    connection_list = service.get_connection_list(8)

    assert connection_list == [{
        'connection_name': 'connection 1',
        'interface1': 'LAN-D',
        'interface2': 'LAN-B'
    }]

def test_get_connection_list_emtpy(mocker):
    utils.get_active_profile.return_value = SimpleNamespace(connections=[])

    connection_list = service.get_connection_list(8)

    assert connection_list == []

def test_add_connection(mocker):
    logical_interfaces = [SimpleNamespace(logical_interface_id=i, logical_name='LAN-' + chr(ord('@') + i)) for i in range(1, 10)]
    interfaces = [InterfaceMockup(interface_id=i + 1,
                                  physical_name=f'eth{i}',
                                  device_id=8,
                                  has_logical_interface=logical_interfaces[i],
                                  logical_name=logical_interfaces[i].logical_name
                                  )
                  for i in range(4)]
    profile = SimpleNamespace(profile_id=8,
                              profile_name='profile 8 name',
                              connections=[]
                              )
    device = DeviceMockup(device_id=8,
                          device_name='test device name',
                          active_profile=9,
                          active_profile_name=profile.profile_name,
                          management_ip='192.168.0.1',
                          interfaces=interfaces,
                          connections=[]
                          )
    utils.get_all_device_info.return_value = device
    utils.get_active_profile.return_value = profile
    utils.get_all_interfaces.return_value = interfaces
    utils.get_logical_interface.side_effect = logical_interfaces
    utils.get_logical_interface_by_name.side_effect = logical_interfaces

    service.update_connections(8, [
        {
            'connection_name': 'connection 1',
            'interface1': 'LAN_A',
            'interface2': 'LAN_B',
            'bandwidth': 500,
            'delay': 10,
            'packet_loss': 30,
            'jitter': 15,
            'corruption': 40,
            'duplication': 50
        }
    ])
    utils.create_connection.assert_called_with('connection 1', logical_interfaces[0], logical_interfaces[1], profile)
    utils.create_parameter.assert_has_calls([call('bandwidth', 500, 1),
                                            call('delay', 10, 1),
                                            call('packet_loss', 30, 1),
                                            call('jitter', 15, 1),
                                            call('corruption', 40, 1),
                                            call('duplication', 50, 1)],
                                            any_order=True)
    salt_api.add_connection.assert_called_with(device.device_name,
                                               'connection 1',
                                               interfaces[0].physical_name,
                                               interfaces[1].physical_name)
    salt_api.update_parameters.assert_called_with(device.device_name,
                                               interfaces[0].physical_name,
                                               {
                                                   'bandwidth': 500,
                                                   'delay': 10,
                                                   'packet_loss': 30,
                                                   'jitter': 15,
                                                   'corruption': 40,
                                                   'duplication': 50
                                               })
    db.session.commit.assert_called_once()
    db.session.rollback.assert_not_called()




def test_delete_connection(mocker):
    logical_interfaces = [SimpleNamespace(logical_interface_id=i,
                                          logical_name='LAN-' + chr(ord('@') + i)) for i in range(1, 10)]
    interfaces = [InterfaceMockup(interface_id=i + 1,
                                  physical_name=f'eth{i}',
                                  device_id=8,
                                  has_logical_interface=logical_interfaces[i],
                                  logical_name=logical_interfaces[i].logical_name
                                  )
                  for i in range(4)]
    connection = ConnectionMockup(
        connection_name='connection 1',
        interface1=logical_interfaces[3].logical_name,
        interface2=logical_interfaces[1].logical_name,
        first_logical_interface=logical_interfaces[3],
        second_logical_interface=logical_interfaces[1],
        active_device_profile=9
    )
    profile = SimpleNamespace(profile_id=8,
                              profile_name='profile 8 name',
                              connections=[
                                  connection
                              ])
    device = DeviceMockup(device_id=8,
                          device_name='test device name',
                          active_profile=9,
                          active_profile_name=profile.profile_name,
                          management_ip='192.168.0.1',
                          interfaces=interfaces,
                          connections=[
                              connection
                          ])
    utils.get_all_device_info.return_value = device
    utils.get_active_profile.return_value = profile
    utils.get_all_interfaces.return_value = interfaces
    utils.get_logical_interface.side_effect = logical_interfaces
    utils.get_logical_interface_by_name.side_effect = logical_interfaces

    service.update_connections(8, [])

    utils.delete_connection.assert_called_with(connection)
    salt_api.remove_connection.assert_called_with(device.device_name, connection.connection_name)
    salt_api.remove_parameters.assert_called_with(device.device_name, interfaces[3].physical_name)
    db.session.commit.assert_called_once()
    db.session.rollback.assert_not_called()

def test_update_connection(mocker):
    logical_interfaces = [SimpleNamespace(logical_interface_id=i,
                                          logical_name='LAN-' + chr(ord('@') + i)) for i in range(1, 10)]
    interfaces = [InterfaceMockup(interface_id=i + 1,
                                  physical_name=f'eth{i}',
                                  device_id=8,
                                  has_logical_interface=logical_interfaces[i],
                                  logical_name=logical_interfaces[i].logical_name
                                  )
                  for i in range(4)]
    parameters = [
        SimpleNamespace(parameter_name='bandwidth', value=500),
        SimpleNamespace(parameter_name='delay', value=10),
        SimpleNamespace(parameter_name='packet_loss', value=30),
        SimpleNamespace(parameter_name='jitter', value=15),
        SimpleNamespace(parameter_name='corruption', value=40),
        SimpleNamespace(parameter_name='duplication', value=50)
    ]
    connection = ConnectionMockup(
        connection_name='connection 1',
        interface1=logical_interfaces[0].logical_name,
        interface2=logical_interfaces[1].logical_name,
        first_logical_interface=logical_interfaces[0],
        second_logical_interface=logical_interfaces[1],
        active_device_profile=9,
        parameters=parameters
    )
    profile = SimpleNamespace(profile_id=8,
                              profile_name='profile 8 name',
                              connections=[
                                  connection
                              ])
    device = DeviceMockup(device_id=8,
                          device_name='test device name',
                          active_profile=9,
                          active_profile_name=profile.profile_name,
                          management_ip='192.168.0.1',
                          interfaces=interfaces,
                          connections=[
                              connection
                          ])
    utils.get_all_device_info.return_value = device
    utils.get_active_profile.return_value = profile
    utils.get_all_interfaces.return_value = interfaces
    utils.get_logical_interface.side_effect = logical_interfaces
    utils.get_logical_interface_by_name.side_effect = logical_interfaces

    service.update_connections(8, [
        {
            'connection_name': 'connection 1',
            'interface1': 'LAN-A',
            'interface2': 'LAN-B',
            'bandwidth': 1000,
            'delay': 11,
            'packet_loss': 50,
            'jitter': 20,
            'corruption': 55,
            'duplication': 10
        }
    ])

    utils.update_parameter.assert_has_calls([
        call(parameters[0], 1000),
        call(parameters[1], 11),
        call(parameters[2], 50),
        call(parameters[3], 20),
        call(parameters[4], 55),
        call(parameters[5], 10)],
        any_order=True)
    salt_api.update_parameters.assert_called_with(
        device.device_name,
        interfaces[0].physical_name,
        {
            'bandwidth': 1000,
            'delay': 11,
            'packet_loss': 50,
            'jitter': 20,
            'corruption': 55,
            'duplication': 10
        })
    db.session.commit.assert_called_once()
    db.session.rollback.assert_not_called()
