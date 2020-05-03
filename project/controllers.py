from core.parser.connection import ConnectionParser
from core.parser.device import DeviceParser
from core.utils import create_device
# Routes

@device_ns.route('/')
class Device(Resource):
    @device_ns.doc('fetch_devices')
    @device_ns.doc(model=device_list_model)
    def get(self):
        '''Fetch a List of Devices with related Information'''
        return get_device_list()

    @device_ns.doc('create_device')
    @device_ns.expect(device_post_model, validate=True)
    @device_ns.marshal_with(device_model, code=201)
    @device_ns.response(400, '{"message": Device <device_name> is already in use!"}')
    def post(self):
        '''Create a new Device'''
        device_name, management_ip = device_parser.parse_arguments()
        try:
            create_device(device_name, management_ip)
        except Exception as e:
            api.abort(*(e.args))
        return device, 201


@device_ns.route('/<int:device_id>/')
@device_ns.param('device_id', 'The device identifier')
class DeviceInformation(Resource):
    @device_ns.doc('fetch_device_information')
    @device_ns.doc(model=device_information_model)
    @device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
    def get(self, device_id):
        '''Fetch a Device Information and Configuration'''
        return get_device(device_id)

    @device_ns.doc('update_connection_config')
    @device_ns.expect(connection_list_model, validate=True)
    @device_ns.doc(model=connection_list_model)
    @device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
    @device_ns.response(400, '{"message": Bad Physical Interface Mapping in {<connection>}!"}')
    def put(self, device_id):
        '''Update Device Connection Configuration'''
        connections = connection_parser.parse_arguments()
        try:
            update_connection(device_id, connections)
        except Exception as e:
            api.abort(*(e.args))

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


@device_ns.route('/<int:device_id>/interfaces/')
@device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
@device_ns.param('device_id', 'The device identifier')
class InterfaceList(Resource):
    @device_ns.doc('fetch_interfaces')
    @device_ns.doc(model=interface_list_model)
    def get(self, device_id):
        '''Fetch all Interfaces of a specific Device'''
        device = get_device(device_id)
        all_interfaces_of_device = get_all_interfaces(device)
        return jsonify(interfaces=[interface.serialize() for interface in all_interfaces_of_device])


@device_ns.route('/<int:device_id>/connections/')
@device_ns.response(404, '{"message": "Device not found"}')
@device_ns.param('device_id', 'The device identifier')
class ConnectionList(Resource):
    @device_ns.doc('fetch_connections')
    @device_ns.doc(model=connection_list_model)
    def get(self, device_id):
        '''Fetch all Connections of a specific Device'''
        device = get_device(device_id)
        active_device_profile = get_active_profile(device)

        return jsonify(connections=[connection.serialize() for connection in active_device_profile.connections])
