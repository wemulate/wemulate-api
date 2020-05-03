from core import db
from core.db.models import ProfileModel, DeviceModel, InterfaceModel, LogicalInterfaceModel, ConnectionModel, ParameterModel

def create_device(device_name, management_ip):
    if(device_exists(device_name)):
        raise Exception(400, f"Device {device_name} is already used!")
    try:
        profile = add_profile_to_db(device_name)
        device = add_device_to_db(device_name, profile.profile_id, management_ip)
        create_device_interfaces(device)
    except Exception as e:
        db.session.rollback()
        raise Exception(500, "Error when creating Device")

def get_device_list():
    all_devices = DeviceModel.query.all()
    return jsonify(devices=[device.serialize() for device in all_devices])

def get_device(device_id)
    device = get_device(device_id)
    active_device_profile = get_active_profile(device)
    all_interfaces_of_device = get_all_interfaces(device)

    data = device.serialize()
    data['interfaces'] = [interface.serialize() for interface in all_interfaces_of_device]
    data['connections'] = [connection.serialize() for connection in active_device_profile.connections]

    return jsonify(data)

def update_connection(device_id, connections):
    device = get_device(device_id)

    active_device_profile = get_active_profile(device)
    active_device_connections = active_device_profile.connections.copy()

    for connection in connections:
        connection_name = connection['connection_name']
        bandwidth_value = connection['bandwidth']
        delay_value = connection['delay']
        packet_loss_value = connection['packet_loss']
        jitter_value = connection['jitter']
        all_parameters = {
            'bandwidth': bandwidth_value,
            'delay': delay_value,
            'packet_loss': packet_loss_value,
            'jitter': jitter_value
        }
        parameters_to_apply = {}
        parameter_changed = False
        interface1_name = connection['interface1']
        interface2_name = connection['interface2']

        logical_interface1 = get_logical_interface(interface1_name)
        logical_interface2 = get_logical_interface(interface2_name)

        physical_interface1_name = get_physical_interface(device, logical_interface1)

        physical_interface2_name = get_physical_interface(device, logical_interface2)

        if(physical_interface1_name is None or physical_interface2_name is None):
            raise Exception(f'Bad Physical Interface Mapping in {connection}!')

        active_connection = get_active_connection(logical_interface1, logical_interface2, active_device_connections)

        try:
            if active_connection is None:
                new_connection = add_connection_to_db(
                    connection_name,
                    logical_interface1,
                    logical_interface2,
                    active_device_profile
                )

                salt_api.add_connection(
                    device.device_name,
                    connection_name,
                    physical_interface1_name,
                    physical_interface2_name
                )

                parameter_changed = add_all_parameters_to_db(
                    all_parameters,
                    new_connection,
                    parameters_to_apply,
                    parameter_changed
                )

            else:
                if(connection_name != active_connection.connection_name):
                    update_connection(
                        device,
                        connection_name,
                        active_connection,
                        physical_interface1_name,
                        physical_interface2_name
                    )

                parameter_changed = update_parameters(
                    all_parameters,
                    active_connection,
                    parameters_to_apply,
                    parameter_changed
                )

                db.session.commit()
                active_device_connections.remove(active_connection)

            # We always define parameters on the first interface of the connection
            interface_to_apply = get_physical_interface(device, logical_interface1)

            if(bandwidth_value == DEFAULT_BANDWITH and delay_value == DEFAULT_DELAY
                and jitter_value == DEFAULT_JITTER and packet_loss_value == DEFAULT_PACKET_LOSS):
                salt_api.remove_parameters(
                    device.device_name,
                    interface_to_apply
                )

            if parameter_changed and parameters_to_apply != {}:
                salt_api.remove_parameters(
                    device.device_name,
                    interface_to_apply
                )

                salt_api.set_parameters(
                    device.device_name,
                    interface_to_apply,
                    parameters_to_apply
                )

        except Exception as e:
            db.session.rollback()

    remove_existing_connections(device, active_device_connections)

    return jsonify(connections=[connection.serialize() for connection in active_device_profile.connections])