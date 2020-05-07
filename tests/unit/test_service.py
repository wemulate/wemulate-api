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
    salt_api.get_interfaces.return_value = {'return': [{'test_device': ['eth1', 'eth2', 'eth3']}]}
    salt_api.get_management_ip.return_value = {'return': [{'test_device': '192.168.0.1'}]}

    mocker.patch.object(utils, 'is_device_present')
    mocker.patch.object(utils, 'create_profile')
    mocker.patch.object(utils, 'create_device')
    mocker.patch.object(utils, 'get_logical_interface')
    mocker.patch.object(utils, 'create_interface')
    utils.is_device_present.return_value = False
    utils.create_profile.return_value = SimpleNamespace(profile_id=9)
    utils.create_device.return_value = SimpleNamespace(device_id=8)
    utils.get_logical_interface.side_effect = [SimpleNamespace(logical_interface_id=1),
                                               SimpleNamespace(logical_interface_id=2),
                                               SimpleNamespace(logical_interface_id=3)]
    utils.create_interface.return_value = {}

    mocker.patch.object(db.session, 'rollback')
    mocker.patch.object(db.session, 'commit')


def test_create_device(mocker):
    service.create_device('test_device')

    salt_api.get_interfaces.assert_called_with('test_device')
    salt_api.get_management_ip.assert_called_with('test_device')

    utils.is_device_present.assert_called_with('test_device')
    utils.create_profile.assert_called_with('test_device')
    utils.create_device.assert_called_with('test_device', 9, '192.168.0.1')
    utils.get_logical_interface.assert_has_calls([call(1), call(2), call(3)])
    utils.create_interface.assert_has_calls([call('eth1', 8, 1), call('eth2', 8, 2), call('eth3', 8, 3)])

    db.session.commit.assert_called_once()
    db.session.rollback.assert_not_called()

