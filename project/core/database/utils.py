from core.database import db
from core.database.models import ProfileModel, DeviceModel, InterfaceModel, \
    LogicalInterfaceModel, ConnectionModel, ParameterModel
from exception import WemulateException
import string


def get_device(device_id):
    device = DeviceModel.query.filter_by(device_id=device_id).first()
    if device is None:
        raise WemulateException(404, f'Device with id {device_id} not found' )
    return device

def get_device_by_name(device_name):
    device = DeviceModel.query.filter_by(device_name=device_name).first()
    if device is None:
        raise WemulateException(404, f'Device with name {device_name} not found' )
    return device

def is_device_present(device_name):
    return DeviceModel.query.filter_by(device_name=device_name).first() is not None

def get_device_list():
    return DeviceModel.query.all()

def get_active_profile(device):
    profile = ProfileModel.query.filter_by(belongs_to_device=device).first()
    if profile is None:
        raise WemulateException(404, f'Profile for device with id {device.device_id} not found!')
    return profile

def get_all_interfaces(device):
    interfaces = InterfaceModel.query.filter_by(belongs_to_device_id=device.device_id).all()
    if not len(interfaces):
        raise WemulateException(404, f'No interfaces for device with id {device.device_id} found!')
    return interfaces

def get_logical_interface(logical_interface_id):
    l_interface = LogicalInterfaceModel.query.filter_by(logical_interface_id=logical_interface_id).first()
    if l_interface is None:
        raise WemulateException(404, f'Logical interface with id {logical_interface_id} not found')
    return l_interface

def get_logical_interface_by_name(logical_interface_name):
    l_interface = LogicalInterfaceModel.query.filter_by(logical_name=logical_interface_name).first()
    if l_interface is None:
        raise WemulateException(404, f'Logical interface with name {logical_interface_name} not found')
    return l_interface

def get_logical_interface_list():
    return LogicalInterfaceModel.query.all()

def get_connection_list():
    return ConnectionModel.query.all()

def create_profile(device_name):
    profile = ProfileModel("default_" + device_name)
    db.session.add(profile)
    db.session.flush()
    return profile

def create_device(device_name, profile_id, management_ip):
    if(management_ip is None):
        device = DeviceModel(device_name, profile_id)
    else:
        device = DeviceModel(device_name, profile_id, management_ip)
    db.session.add(device)
    db.session.flush()
    return device

def create_connection(connection_name, logical_interface1, logical_interface2, active_device_profile):
    connection = ConnectionModel(
        connection_name,
        logical_interface1.logical_interface_id,
        logical_interface2.logical_interface_id,
        active_device_profile.profile_id
    )
    db.session.add(connection)
    db.session.flush()
    return connection

def create_parameter(parameter_name, value, connection_id):
    parameter = ParameterModel(
        parameter_name,
        value,
        connection_id
    )
    db.session.add(parameter)
    db.session.flush()
    return parameter

def create_interface(physical_name, device_id, logical_interface_id):
    interface = InterfaceModel(physical_name, device_id, logical_interface_id)
    db.session.add(interface)
    db.session.flush()
    return interface

def update_parameter(parameter, value):
    if parameter.value == value:
        return False
    parameter.value = value
    db.session.add(parameter)
    db.session.flush()
    return True

def update_connection(connection, connection_name):
    if connection.connection_name == connection_name:
        return False
    connection.connection_name = connection_name
    db.session.add(connection)
    db.session.flush()
    return True

def delete_connection(connection):
    db.session.delete(connection)
    db.session.flush()

def create_logical_interfaces():
    for character in list(string.ascii_uppercase):
        logical_interface = LogicalInterfaceModel("LAN-" + character)
        db.session.add(logical_interface)
    db.session.flush()

def delete_present_connection():
    try:
        db.session.query(ConnectionModel).delete()
        db.session.commit()
    except:
        print('Flushing Connection Table')
        
