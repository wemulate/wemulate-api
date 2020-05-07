import sys
import os
import pytest

path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{path}/../../project')

from core import create_app
from core.database import db
from core.database.models import ProfileModel, DeviceModel, InterfaceModel, LogicalInterfaceModel
from core.database.models import ConnectionModel, ParameterModel, OnOffTimerModel
import core.database.utils as dbutils


''' ##### Prerequisites ##### '''

''' ADD env var: export POSTGRES_USER=wemulate POSTGRES_PASSWORD=wemulateEPJ2020 POSTGRES_DB=wemulate POSTGRES_HOST=localhost POSTGRES_PORT=5432 SALT_API=http://localhost:8000 SALT_PASSWORD='EPJ@2020!!' WEMULATE_TESTING='True' '''

''' RUN TEST with ` pytest -v test_db_models.py --disable-pytest-warnings` '''

''' ##### Create DB and necessary parts ##### '''

app, api = create_app()


@pytest.fixture(autouse=True)
def recreate_database():
    db.drop_all()
    db.create_all()
    if not len(dbutils.get_logical_interface_list()):
        dbutils.create_logical_interfaces()
        db.session.commit()

''' ##### Helper Functions ##### '''
def commit_to_database(object_to_add):
    db.session.add(object_to_add)
    db.session.commit()

def create_profile(profile_name):
    profile_to_add = ProfileModel(profile_name)
    commit_to_database(profile_to_add)
    return profile_to_add

def find_profile_in_database(profile_id):
    return ProfileModel.query.filter_by(profile_id=profile_id).first()

def compare_profile(profile1, profile2):
    return (profile1.profile_id == profile2.profile_id
            and profile1.profile_name == profile2.profile_name)

def create_device(device_name, profile_id):
    device_to_add = DeviceModel(device_name, profile_id)
    commit_to_database(device_to_add)
    return device_to_add

def find_device_in_database(device_id):
    return DeviceModel.query.filter_by(device_id=device_id).first()

def compare_device(device1, device2, profile):
    return (device1.device_name == device2.device_name
            and device1.active_profile_id == device2.active_profile_id == profile.profile_id)

def create_interface(physical_name, device_id, logical_interface_id=None):
    if logical_interface_id:
        interface_to_add = InterfaceModel(physical_name, device_id, logical_interface_id)
    else:
        interface_to_add = InterfaceModel(physical_name, device_id)
    commit_to_database(interface_to_add)
    return interface_to_add

def find_interface_in_database(interface_id):
    return InterfaceModel.query.filter_by(interface_id=interface_id).first()

def compare_interface(interface1, interface2, device):
    if interface1.has_logical_interface_id is not None and interface2.has_logical_interface_id is not None:
        return (interface1.belongs_to_device_id == interface2.belongs_to_device_id == device.device_id
        and interface1.physical_name == interface2.physical_name
        and interface1.has_logical_interface_id == interface2.has_logical_interface_id)
    else:
        return (interface1.belongs_to_device_id == interface2.belongs_to_device_id == device.device_id
               and interface1.physical_name == interface2.physical_name)

def create_logical_interface(logical_name):
    logical_interface_to_add = LogicalInterfaceModel(logical_name)
    commit_to_database(logical_interface_to_add)
    return logical_interface_to_add

def find_logical_interface_in_database(logical_interface_id):
    return LogicalInterfaceModel.query.filter_by(logical_interface_id=logical_interface_id).first()

def compare_logical_interface(logical_interface1, logical_interface2):
    return (logical_interface1.logical_interface_id == logical_interface2.logical_interface_id
            and logical_interface1.logical_name == logical_interface2.logical_name)

def create_connection(connection_name, first_logical_interface_id, second_logical_interface_id, profile_id):
    connection_to_add = ConnectionModel(connection_name, first_logical_interface_id, second_logical_interface_id, profile_id)
    commit_to_database(connection_to_add)
    return connection_to_add

def find_connection_in_database(connection_id):
    return ConnectionModel.query.filter_by(connection_id=connection_id).first()

def compare_connection(connection1, connection2, profile):
    return(connection1.connection_id == connection2.connection_id
           and connection1.connection_name == connection2.connection_name
           and connection1.bidirectional == connection2.bidirectional
           and connection1.first_logical_interface_id == connection2.first_logical_interface_id
           and connection1.second_logical_interface_id == connection2.second_logical_interface_id
           and connection1.belongs_to_profile_id == connection2.belongs_to_profile_id)

def create_parameter(parameter_name, value, connection_id, on_off_timer_id=None):
    if on_off_timer_id is None:
        parameter_to_add = ParameterModel(parameter_name, value, connection_id)
    else:
        parameter_to_add = ParameterModel(parameter_name, value, connection_id, on_off_timer_id)
    commit_to_database(parameter_to_add)
    return parameter_to_add

def find_parameter_in_database(parameter_id):
    return ParameterModel.query.filter_by(parameter_id=parameter_id).first()

def compare_parameter(parameter1, parameter2, connection):
    return(parameter1.parameter_id == parameter2.parameter_id and parameter1.parameter_name == parameter2.parameter_name
           and parameter1.value == parameter2.value
           and parameter1.belongs_to_connection_id == parameter2.belongs_to_connection_id
           and parameter1.belongs_to_connection_id == connection.connection_id and parameter1.active == parameter2.active)

''' ##### Test Functions ##### '''
def test_create_profile():
    test_profile = create_profile("test_profile")
    profile_from_db = find_profile_in_database(test_profile.profile_id)
    assert compare_profile(test_profile, profile_from_db)

def test_update_profile():
    test_profile = create_profile("initial_value")
    profile_from_db = find_profile_in_database(test_profile.profile_id)
    test_profile.profile_name = "new_content"
    commit_to_database(test_profile)
    assert compare_profile(test_profile, profile_from_db)
    profile_from_db.connection_name = "newer_content"
    commit_to_database(profile_from_db)
    assert compare_profile(test_profile, profile_from_db)

def test_create_device_without_interfaces():
    test_profile = create_profile("default-wemulate")
    test_device = create_device("wemulate", test_profile.profile_id)
    device_from_db = find_device_in_database(test_device.device_id)
    assert compare_device(test_device, device_from_db, test_profile)
    # Test if management ip == local loopback address because no mgmt ip was set
    assert device_from_db.management_ip == '127.0.0.1'

def test_create_interface_without_logical_interface():
    test_profile = create_profile("default-wemulate")
    test_device = create_device("wemulate", test_profile.profile_id)
    test_interface = create_interface("ens123", test_device.device_id)
    interface_from_db = find_interface_in_database(test_interface.interface_id)
    assert compare_interface(test_interface, interface_from_db, test_device)

def test_create_logical_interface():
    test_logical_interface = create_logical_interface("LAN A")
    logical_interface_from_db = find_logical_interface_in_database(test_logical_interface.logical_interface_id)
    assert compare_logical_interface(test_logical_interface, logical_interface_from_db)

def test_create_interface_with_logical_interface():
    test_profile = create_profile("profile1")
    test_device = create_device("wemulate-host1", test_profile.profile_id)
    test_logical_interface = create_logical_interface("LAN B")
    test_interface = create_interface("ens1234567", test_device.device_id, test_logical_interface.logical_interface_id)
    interface_from_db = find_interface_in_database(test_interface.interface_id)
    assert compare_interface(test_interface, interface_from_db, test_device)

def test_create_connection_without_parameter():
    test_profile = create_profile("profile2")
    test_logical_interface1 = create_logical_interface("LAN A")
    test_logical_interface2 = create_logical_interface("LAN B")
    connection_name = test_logical_interface1.logical_name + " to " + test_logical_interface2.logical_name
    test_connection = create_connection(connection_name, test_logical_interface1.logical_interface_id,
                                        test_logical_interface2.logical_interface_id, test_profile.profile_id)
    connection_from_db = find_connection_in_database(test_connection.connection_id)
    assert compare_connection(test_connection, connection_from_db, test_profile)

def test_create_parameter():
    test_profile = create_profile("profile3")
    test_logical_interface1 = create_logical_interface("LAN C ")
    test_logical_interface2 = create_logical_interface("LAN D")

    connection_name = test_logical_interface1.logical_name + " to " + test_logical_interface2.logical_name
    test_connection = create_connection(connection_name, test_logical_interface1.logical_interface_id,
                                        test_logical_interface2.logical_interface_id, test_profile.profile_id)
    test_parameter = create_parameter("delay", 100, test_connection.connection_id)
    parameter_from_db = find_parameter_in_database(test_parameter.parameter_id)
    assert compare_parameter(test_parameter, parameter_from_db, test_connection)
