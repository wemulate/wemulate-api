from core.database.models import ProfileModel, DeviceModel, InterfaceModel, LogicalInterfaceModel, ConnectionModel, ParameterModel
import string

class DBUtils:

    def __init__(self, db):
        self.db = db
        self.__create_logical_interfaces()
            
    def get_device(self, device_id):
        return DeviceModel.query.filter_by(device_id=device_id).first_or_404(description="Device not found!")

    def get_device_list(self):
        return DeviceModel.query.all()

    def get_active_profile(self, device):
        return ProfileModel.query.filter_by(belongs_to_device=device).first_or_404(description='Profile not found!')

    def get_all_interfaces(self, device):
        return InterfaceModel.query.filter_by(belongs_to_device_id=device.device_id).all()

    def get_logical_interface(self, logical_interface_id):
        return LogicalInterfaceModel.query.filter_by(logical_interface_id=logical_interface_id).first()

    def get_logical_interface_by_name(self, logical_interface_name):
        return LogicalInterfaceModel.query.filter_by(logical_name=logical_interface_name).first()

    def device_exists(self, device_name):
        device_exists = DeviceModel.query.filter_by(device_name=device_name).first()
        return device_exists

    def create_profile(self, device_name):
        profile = ProfileModel("default_" + device_name)
        self.db.session.add(profile)
        return profile

    def create_device(self, device_name, profile_id, management_ip):
        if(management_ip is None):
            device = DeviceModel(device_name, profile_id)
        else:
            device = DeviceModel(device_name, profile_id, management_ip)
        self.db.session.add(device)
        return device

    def create_connection(self, connection_name, logical_interface1, logical_interface2, active_device_profile):
        connection = ConnectionModel(
            connection_name,
            logical_interface1.logical_interface_id,
            logical_interface2.logical_interface_id,
            active_device_profile.profile_id
        )
        self.db.session.add(connection)
        return connection

    def create_parameter(self, parameter_name, value, connection_id):
        parameter = ParameterModel(
            parameter_name,
            value,
            connection_id
        )
        self.db.session.add(parameter)
        return parameter

    def create_interface(self, physical_name, device_id, logical_interface_id):
        interface = InterfaceModel(physical_name, device_id, logical_interface_id)
        self.db.session.add(interface)
        return interface

    def update_parameter(self, parameter, value):
        if parameter.value == value:
            return False
        parameter.value = value
        self.db.session.add(parameter)
        return True

    def update_connection(self, connection, connection_name):
        if connection.connection_name == connection_name:
            return False
        connection.connection_name = connection_name
        self.db.session.add(connection)
        return True

    def delete_connection(self, connection):
        self.db.session.remove(connection)

    
    def __create_logical_interfaces(self):
        for character in list(string.ascii_uppercase):
            logical_interface = LogicalInterfaceModel("LAN-" + character)
            self.db.session.add(logical_interface)
