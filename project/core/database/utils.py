from core import db
from core.database.models import ProfileModel, DeviceModel, InterfaceModel, \
    LogicalInterfaceModel, ConnectionModel, ParameterModel
import string

def get_device(device_id):
    return DeviceModel.query.filter_by(device_id=device_id).first_or_404(description="Device not found!")

def get_device_list(self):
    return DeviceModel.query.all()

def get_active_profile(device):
    return ProfileModel.query.filter_by(belongs_to_device=device).first_or_404(description='Profile not found!')

def get_all_interfaces(device):
    return InterfaceModel.query.filter_by(belongs_to_device_id=device.device_id).all()

def get_logical_interface(logical_interface_id):
    return LogicalInterfaceModel.query.filter_by(logical_interface_id=logical_interface_id).first()

def get_logical_interface_by_name(logical_interface_name):
    return LogicalInterfaceModel.query.filter_by(logical_name=logical_interface_name).first()

def device_exists(device_name):
    device_exists = DeviceModel.query.filter_by(device_name=device_name).first()
    return device_exists

def create_profile(device_name):
    profile = ProfileModel("default_" + device_name)
    db.session.add(profile)
    return profile

def create_device(device_name, profile_id, management_ip):
    if(management_ip is None):
        device = DeviceModel(device_name, profile_id)
    else:
        device = DeviceModel(device_name, profile_id, management_ip)
    db.session.add(device)
    return device

def create_connection(connection_name, logical_interface1, logical_interface2, active_device_profile):
    connection = ConnectionModel(
        connection_name,
        logical_interface1.logical_interface_id,
        logical_interface2.logical_interface_id,
        active_device_profile.profile_id
    )
    db.session.add(connection)
    return connection

def create_parameter(parameter_name, value, connection_id):
    parameter = ParameterModel(
        parameter_name,
        value,
        connection_id
    )
    db.session.add(parameter)
    return parameter

def create_interface(physical_name, device_id, logical_interface_id):
    interface = InterfaceModel(physical_name, device_id, logical_interface_id)
    db.session.add(interface)
    return interface

def update_parameter(parameter, value):
    if parameter.value == value:
        return False
    parameter.value = value
    db.session.add(parameter)
    return True

def update_connection(connection, connection_name):
    if connection.connection_name == connection_name:
        return False
    connection.connection_name = connection_name
    db.session.add(connection)
    return True

def delete_connection(connection):
    db.session.remove(connection)

def create_logical_interfaces():
    for character in list(string.ascii_uppercase):
        logical_interface = LogicalInterfaceModel("LAN-" + character)
        db.session.add(logical_interface)
