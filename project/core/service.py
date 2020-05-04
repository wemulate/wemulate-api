from core.database.utils import DBUtils

# Default Interface Parameters
DEFAULT_PARAMETERS = {
    'bandwidth': 1000,
    'delay': 0,
    'jitter': 0,
    'packet_loss': 0,
    'corruption': 0,
    'duplication': 0
}

class WemulateService:

    def __init__ (self, db, salt_api):
        self.db = db
        self.dbutils = DBUtils(db)
        self.salt = salt_api
        self.db.session.commit()

    def create_device(self, device_name, management_ip):
        if(self.dbutils.device_exists(device_name)):
            raise Exception(400, f"Device {device_name} is already used!")
        try:
            # Return Format: {'return': [{'wemulate_host1': ['enp0s31f6', "eth0", "eth1"]}]}
            salt_return = self.salt.get_interfaces(device_name)
            physical_interface_names = salt_return['return'][0][device_name]

            profile = self.dbutils.create_profile(device_name)
            device = self.dbutils.create_device(device_name, profile.profile_id, management_ip)

            interface_id = 1
            for physical_name in physical_interface_names:
                logical_interface = self.dbutils.get_logical_interface(interface_id)
                self.dbutils.create_interface(physical_name, device.device_id, logical_interface.logical_interface_id)
                interface_id += 1
            
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise Exception(500, "Error when creating device: " + str(e.args))

        return device

    def get_device_list(self):
        try:
            devices = self.dbutils.get_device_list()
        except Exception as e:
            raise Exception(500, "Error when getting device list: " + str(e.args))

        return [device.serialize() for device in devices]

    def get_device(self, device_id):
        try:
            device = self.dbutils.get_device(device_id)
            active_device_profile = self.dbutils.get_active_profile(device)
            all_interfaces_of_device = self.dbutils.get_all_interfaces(device)
        except Exception as e:
            raise Exception(500, "Error when getting device: " + str(e.args))

        data = device.serialize()
        data['interfaces'] = [interface.serialize() for interface in all_interfaces_of_device]
        data['connections'] = [connection.serialize() for connection in active_device_profile.connections]
        return data

    def get_interface_list(self, device):
        try:
            interfaces = self.dbutils.get_all_interfaces(device)
        except Exception as e:
            raise Exception(500, "Error when getting interface list: " + str(e.args))

        return [interface.serialize() for interface in interfaces]

    def get_connection_list(self, device):
        try:
            profile = self.dbutils.get_active_profile(device)
        except Exception as e:
            raise Exception(500, "Error when getting connection list: " + str(e.args))

        return [connection.serialize() for connection in profile.connections]

    def update_connection(self, device_id, connections):
        device = self.dbutils.get_device(device_id)

        active_device_profile = self.dbutils.get_active_profile(device)
        old_connections = active_device_profile.connections.copy()

        for connection in connections:
            connection_name = connection['connection_name']
            parameters = {
                'bandwidth': connection['bandwidth'],
                'delay': connection['delay'],
                'packet_loss': connection['packet_loss'],
                'jitter': connection['jitter'],
                'corruption': connection['corruption'],
                'duplication': connection['duplication']
            }
            parameters_to_apply = {}
            parameter_changed = False
            interface1_name = connection['interface1']
            interface2_name = connection['interface2']

            logical_interface1 = self.dbutils.get_logical_interface_by_name(interface1_name)
            logical_interface2 = self.dbutils.get_logical_interface_by_name(interface2_name)

            physical_interface1_name = self.__get_physical_interface(device, logical_interface1)
            physical_interface2_name = self.__get_physical_interface(device, logical_interface2)
            if(physical_interface1_name is None or physical_interface2_name is None):
                raise Exception(500, f'Bad Physical Interface Mapping in {connection}!')

            active_connection = self.__get_active_connection(logical_interface1, logical_interface2, old_connections)

            try:
                if active_connection is None:
                    self.dbutils.create_connection(
                        connection_name,
                        logical_interface1,
                        logical_interface2,
                        active_device_profile
                    )

                    self.salt.add_connection(
                        device.device_name,
                        connection_name,
                        physical_interface1_name,
                        physical_interface2_name
                    )

                    for key, value in parameters.items():
                        self.dbutils.create_parameter(
                            key,
                            value,
                            connection.connection_id
                        )
                        if(value != DEFAULT_PARAMETERS[key]):
                            parameters_to_apply[key] = value

                    parameter_changed = True

                else:
                    if(connection_name != active_connection.connection_name):
                        self.dbutils.update_connection(active_connection, connection_name)

                        self.salt.remove_connection(
                            device.device_name,
                            active_connection.connection_name
                        )
                        self.salt.add_connection(
                            device.device_name,
                            connection_name,
                            physical_interface1_name,
                            physical_interface2_name
                        )
                    
                    for parameter in active_connection.parameters:
                        if self.dbutils.update_parameter(parameter, parameters[parameter.parameter_name]):
                            parameter_changed = True
                        if parameters[parameter.parameter_name] != DEFAULT_PARAMETERS[parameter.parameter_name]:
                            parameters_to_apply[parameter.parameter_name] = parameters[parameter.parameter_name]

                    old_connections.remove(active_connection)

                # We always define parameters on the first interface of the connection
                interface_to_apply = self.__get_physical_interface(device, logical_interface1)

                if parameter_changed:
                    self.salt.remove_parameters(
                        device.device_name,
                        interface_to_apply
                    )

                    if parameters_to_apply != {}:
                        self.salt.set_parameters(
                            device.device_name,
                            interface_to_apply,
                            parameters_to_apply
                        )
                
                for connection in old_connections:
                    self.__delete_connection(device, connection)

                self.db.session.commit()
            except Exception:
                self.db.session.rollback()
                raise Exception(500, 'Error when updating connection')

        return [connection.serialize() for connection in active_device_profile.connections]


    # Helper Functions

    def __get_active_connection(self, logical_interface1, logical_interface2, active_device_connections):
        return next(
                (connection for connection in active_device_connections
                    if connection.first_logical_interface is logical_interface1
                    and connection.second_logical_interface is logical_interface2), None
        )


    def __get_physical_interface(self, device, logical_interface):
        return next(
                (interface.physical_name for interface in device.interfaces
                    if interface.has_logical_interface is logical_interface), None
        )

    def __delete_connection(self, device, connection):

        self.dbutils.delete_connection(connection)

        interface = self.__get_physical_interface(
            device,
            connection.first_logical_interface
        )
        self.salt.remove_parameters(device.device_name, interface)
        self.salt.remove_connection(
            device.device_name,
            connection.connection_name
        )




