from core import db, salt_api
import core.database.utils as dbutils

def create_device(device_name, management_ip):
    if(dbutils.get_device_by_name(device_name)):
        raise Exception(400, f"Device {device_name} is already registered!")
    try:
        # Return Format: {'return': [{'wemulate_host1': ['enp0s31f6', "eth0", "eth1"]}]}
        salt_return = salt_api.get_interfaces(device_name)
        physical_interface_names = salt_return['return'][0][device_name]

        profile = dbutils.create_profile(device_name)
        device = dbutils.create_device(device_name, profile.profile_id, management_ip)

        interface_id = 1
        for physical_name in physical_interface_names:
            logical_interface = dbutils.get_logical_interface(interface_id)
            dbutils.create_interface(physical_name, device.device_id, logical_interface.logical_interface_id)
            interface_id += 1

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception(500, "Error when creating device: " + str(e.args))

    return device

def get_device_list():
    try:
        devices = dbutils.get_device_list()
    except Exception as e:
        raise Exception(500, "Error when getting device list: " + str(e.args))

    return [device.serialize() for device in devices]

def get_device(device_id):
    try:
        device = dbutils.get_device(device_id)
        active_device_profile = dbutils.get_active_profile(device)
        all_interfaces_of_device = dbutils.get_all_interfaces(device)
    except Exception as e:
        raise Exception(500, "Error when getting device: " + str(e.args))

    data = device.serialize()
    data['interfaces'] = [interface.serialize() for interface in all_interfaces_of_device]
    data['connections'] = [connection.serialize() for connection in active_device_profile.connections]
    return data

def get_interface_list(device):
    try:
        interfaces = dbutils.get_all_interfaces(device)
    except Exception as e:
        raise Exception(500, "Error when getting interface list: " + str(e.args))

    return [interface.serialize() for interface in interfaces]

def get_connection_list(device):
    try:
        profile = dbutils.get_active_profile(device)
    except Exception as e:
        raise Exception(500, "Error when getting connection list: " + str(e.args))

    return [connection.serialize() for connection in profile.connections]

def update_connection(device_id, connections):
    device = dbutils.get_device(device_id)

    active_device_profile = dbutils.get_active_profile(device)
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
        parameter_changed = False
        interface1_name = connection['interface1']
        interface2_name = connection['interface2']

        logical_interface1 = dbutils.get_logical_interface_by_name(interface1_name)
        logical_interface2 = dbutils.get_logical_interface_by_name(interface2_name)

        physical_interface1_name = __get_physical_interface(device, logical_interface1)
        physical_interface2_name = __get_physical_interface(device, logical_interface2)
        if(physical_interface1_name is None or physical_interface2_name is None):
            raise Exception(500, f'Bad Physical Interface Mapping in {connection}!')

        active_connection = __get_active_connection(logical_interface1, logical_interface2, old_connections)

        try:
            if active_connection is None:
                dbutils.create_connection(connection_name, logical_interface1, logical_interface2,
                                          active_device_profile)
                salt_api.add_connection(device.device_name, connection_name, physical_interface1_name,
                                        physical_interface2_name)

                for key, value in parameters.items():
                    dbutils.create_parameter(key, value, connection.connection_id)

                parameter_changed = True

            else:
                if(connection_name != active_connection.connection_name):
                    dbutils.update_connection(active_connection, connection_name)
                    salt_api.update_connection(device.device_name, connection_name, physical_interface1_name,
                                               physical_interface2_name)

                for parameter in active_connection.parameters:
                    if dbutils.update_parameter(parameter, parameters[parameter.parameter_name]):
                        parameter_changed = True

                old_connections.remove(active_connection)

            # We always define parameters on the first interface of the connection
            interface_to_apply = __get_physical_interface(device, logical_interface1)

            if parameter_changed:
                salt_api.update_parameters(device.device_name, interface_to_apply, parameters)

            for connection in old_connections:
                __delete_connection(device, connection)

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception(500, 'Error when updating connection')

    return [connection.serialize() for connection in active_device_profile.connections]

# Helper Functions

def __get_active_connection(logical_interface1, logical_interface2, active_device_connections):
    return next(
        (connection for connection in active_device_connections
            if connection.first_logical_interface is logical_interface1 and
            connection.second_logical_interface is logical_interface2), None
    )

def __get_physical_interface(device, logical_interface):
    return next(
        (interface.physical_name for interface in device.interfaces
            if interface.has_logical_interface is logical_interface), None
    )

def __delete_connection(device, connection):

    dbutils.delete_connection(connection)

    interface = __get_physical_interface(
        device,
        connection.first_logical_interface
    )
    salt_api.remove_parameters(device.device_name, interface)
    salt_api.remove_connection(
        device.device_name,
        connection.connection_name
    )
