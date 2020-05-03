from flask_restplus import Resource, fields
from flask import jsonify
from core import db, create_app
from apis import create_salt_api
from core.parser.connection import ConnectionParser
from core.parser.device import DeviceParser
from core.models import ProfileModel, DeviceModel, InterfaceModel, LogicalInterfaceModel, ConnectionModel, ParameterModel
# , OnOffTimerModel
from core.logical_interface import create_logical_interfaces

# Default Interface Parameters

DEFAULT_BANDWITH = 1000
DEFAULT_DELAY = 0
DEFAULT_JITTER = 0
DEFAULT_PACKET_LOSS = 0
DEFAULT_CORRUPTION = 0
DEFAULT_DUPLICATION = 0


app, api, device_ns = create_app()
salt_api = create_salt_api()
create_logical_interfaces()
device_parser = DeviceParser(api)
connection_parser = ConnectionParser(api)

# Models

device_model = api.model('device_model', {
    'active_profile_name': fields.String(attribute='active_profile.profile_name'),
    'device_id': fields.Integer,
    'device_name': fields.String,
    'management_ip': fields.String,
})


device_list_model = api.model('device_list_model', {
    'devices': fields.List(fields.Nested(device_model)),
})


device_post_model = api.model('device_post_model', {
    'device_name': fields.String(required=True),
    'management_ip': fields.String
})

interface_model = api.model('interface_model', {
    'interface_id': fields.Integer,
    'logical_name': fields.String(attribute='has_logical_interface.logical_name'),
    'physical_name': fields.String,
})


interface_list_model = api.model('interface_list_model', {
    'interfaces': fields.List(fields.Nested(interface_model)),
})

connection_model = api.model('connection_model', {
    'connection_name': fields.String,
    'interface1': fields.String,
    'interface2': fields.String,
    'delay': fields.Integer,
    'packet_loss': fields.Integer,
    'bandwidth': fields.Integer,
    'jitter': fields.Integer
})

connection_list_model = api.model('connection_list_model', {
    'connections': fields.List(fields.Nested(connection_model)),
})

device_information_model = api.model('device_information_model', {
    'active_profile_name': fields.String(attribute='active_profile.profile_name'),
    'device_id': fields.Integer,
    'device_name': fields.String,
    'management_ip': fields.String,
    'connections': fields.List(fields.Nested(connection_model)),
    'interfaces': fields.List(fields.Nested(interface_model)),
})

# Helper Functions



def device_exists(device_name):
    device_exists = DeviceModel.query.filter_by(device_name=device_name).first()
    return device_exists


def add_profile_to_db(device_name):
    profile_to_add = ProfileModel("default_" + device_name)
    db.session.add(profile_to_add)
    db.session.commit()
    return profile_to_add


def add_device_to_db(device_name, profile_id, management_ip):
    if(management_ip is None):
        device = DeviceModel(device_name, profile_id)
    else:
        device = DeviceModel(device_name, profile_id, management_ip)
    db.session.add(device)
    db.session.commit()
    return device


def create_device_interfaces(device):
    # Return Format: {'return': [{'wemulate_host1': ['enp0s31f6', "eth0", "eth1"]}]}
    salt_return = salt_api.get_interfaces(device.device_name)
    physical_interface_names = salt_return['return'][0][device.device_name]
    interface_number = 1
    for physical_name in physical_interface_names:
        logical_interface = LogicalInterfaceModel.query.filter_by(logical_interface_id=interface_number).first()
        interface = InterfaceModel(physical_name, device.device_id, logical_interface.logical_interface_id)
        interface_number += 1
        db.session.add(logical_interface)
        db.session.add(interface)
        db.session.commit()


def get_device(device_id):
    return DeviceModel.query.filter_by(device_id=device_id).first_or_404(description="Device not found!")


def get_active_profile(device):
    return ProfileModel.query.filter_by(belongs_to_device=device).first_or_404(description='Profile not found!')


def get_all_interfaces(device):
    return InterfaceModel.query.filter_by(belongs_to_device_id=device.device_id).all()


def get_logical_interface(logical_interface_name):
    return LogicalInterfaceModel.query.filter_by(logical_name=logical_interface_name).first()


def get_active_connection(logical_interface1, logical_interface2, active_device_connections):
    return next(
               (connection for connection in active_device_connections
                if connection.first_logical_interface is logical_interface1
                and connection.second_logical_interface is logical_interface2), None
    )


def get_physical_interface(device, logical_interface):
    return next(
               (interface.physical_name for interface in device.interfaces
                if interface.has_logical_interface is logical_interface), None
    )


def add_connection_to_db(connection_name, logical_interface1, logical_interface2, active_device_profile):
    connection_to_add = ConnectionModel(
        connection_name,
        logical_interface1.logical_interface_id,
        logical_interface2.logical_interface_id,
        active_device_profile.profile_id
    )
    db.session.add(connection_to_add)
    db.session.commit()
    return connection_to_add


def add_all_parameters_to_db(all_parameters, connection, parameters_to_apply, parameter_changed):
    for key, value in all_parameters.items():
        if(key == 'bandwidth'):
            add_parameter_to_db(
                'bandwidth',
                value,
                connection.connection_id
            )
            if(value != DEFAULT_BANDWITH):
                parameters_to_apply['bandwidth'] = value

        if(key == 'delay'):
            add_parameter_to_db(
                'delay',
                value,
                connection.connection_id
            )
            if(value != DEFAULT_DELAY):
                parameters_to_apply['delay'] = value

        if(key == 'packet_loss'):
            add_parameter_to_db(
                'packet_loss',
                value,
                connection.connection_id
            )
            if(value != DEFAULT_JITTER):
                parameters_to_apply['packet_loss'] = value

        if(key == 'jitter'):
            add_parameter_to_db(
                'jitter',
                value,
                connection.connection_id
            )
            if(value != DEFAULT_PACKET_LOSS):
                parameters_to_apply['jitter'] = value

        if(key == 'corruption'):
            add_parameter_to_db(
                'corruption',
                value,
                connection.connection_id
            )
            if(value != DEFAULT_CORRUPTION):
                parameters_to_apply['corruption'] = value

        if(key == 'duplication'):
            add_parameter_to_db(
                'duplication',
                value,
                connection.connection_id
            )
            if(value != DEFAULT_DUPLICATION):
                parameters_to_apply['duplication'] = value

    db.session.commit()
    parameter_changed = True
    return parameter_changed


def add_parameter_to_db(parameter_name, value, connection_id):
    parameter_to_add = ParameterModel(
        parameter_name,
        value,
        connection_id
    )
    db.session.add(parameter_to_add)


def update_connection(
    device,
    new_connection_name,
    active_connection,
    physical_interface1_name,
    physical_interface2_name
):
    salt_api.remove_connection(
        device.device_name,
        active_connection.connection_name
    )
    salt_api.add_connection(
        device.device_name,
        new_connection_name,
        physical_interface1_name,
        physical_interface2_name
    )
    active_connection.connection_name = new_connection_name
    db.session.add(active_connection)


def update_parameters(all_parameters, active_connection, parameters_to_apply, parameter_changed):
    actual_bandwidth = next(
        parameter for parameter in active_connection.parameters
        if parameter.parameter_name == 'bandwidth')
    actual_delay = next(
        parameter for parameter in active_connection.parameters
        if parameter.parameter_name == 'delay'
    )
    actual_jitter = next(
        parameter for parameter in active_connection.parameters
        if parameter.parameter_name == 'jitter'
    )
    actual_packet_loss = next(
        parameter for parameter in active_connection.parameters
        if parameter.parameter_name == 'packet_loss'
    )

    actual_corruption = next(
        parameter for parameter in active_connection.parameters
        if parameter.parameter_name == 'corruption'
    )

    actual_duplication = next(
        parameter for parameter in active_connection.parameters
        if parameter.parameter_name == 'duplication'
    )

    for key, value in all_parameters.items():
        if(key == 'bandwidth'):
            if(value != actual_bandwidth.value):
                actual_bandwidth.value = value
                parameter_changed = True
                db.session.add(actual_bandwidth)
            if(value != 1000):
                parameters_to_apply['bandwidth'] = value

        if(key == 'delay'):
            if(value != actual_delay.value):
                actual_delay.value = value
                parameter_changed = True
                db.session.add(actual_delay)
            if(value != 0):
                parameters_to_apply['delay'] = value

        if(key == 'jitter'):
            if(value != actual_jitter.value):
                actual_jitter.value = value
                parameter_changed = True
                db.session.add(actual_jitter)
            if(value != 0):
                parameters_to_apply['jitter'] = value

        if(key == 'packet_loss'):
            if(value != actual_packet_loss.value):
                actual_packet_loss.value = value
                parameter_changed = True
                db.session.add(actual_packet_loss)
            if(value != 0):
                parameters_to_apply['packet_loss'] = value

        if(key == 'corruption'):
            if(value != actual_corruption.value):
                actual_corruption.value = value
                parameter_changed = True
                db.session.add(actual_corruption)
            if(value != 0):
                parameters_to_apply['corruption'] = value

        if(key == 'duplication'):
            if(value != actual_duplication.value):
                actual_duplication.value = value
                parameter_changed = True
                db.session.add(actual_duplication)
            if(value != 0):
                parameters_to_apply['duplication'] = value
    return parameter_changed


def remove_existing_connections(device, active_device_connections):
    for connection_to_delete in active_device_connections:
        interface_to_remove_parameter = get_physical_interface(
            device,
            connection_to_delete.first_logical_interface
        )

        salt_api.remove_parameters(device.device_name, interface_to_remove_parameter)

        db.session.delete(connection_to_delete)
        salt_api.remove_connection(
            device.device_name,
            connection_to_delete.connection_name
        )
        db.session.commit()
# Routes


@device_ns.route('/')
class Device(Resource):
    @device_ns.doc('fetch_devices')
    @device_ns.doc(model=device_list_model)
    def get(self):
        '''Fetch a List of Devices with related Information'''
        all_devices = DeviceModel.query.all()
        return jsonify(devices=[device.serialize() for device in all_devices])

    @device_ns.doc('create_device')
    @device_ns.expect(device_post_model, validate=True)
    @device_ns.marshal_with(device_model, code=201)
    @device_ns.response(400, '{"message": Device <device_name> is already in use!"}')
    def post(self):
        '''Create a new Device'''
        device_name, management_ip = device_parser.parse_arguments()
        if(device_exists(device_name)):
            api.abort(400, f"Device {device_name} is already used!")
        try:
            profile = add_profile_to_db(device_name)
            device = add_device_to_db(device_name, profile.profile_id, management_ip)
            create_device_interfaces(device)
        except Exception:
            db.session.rollback()
        return device, 201


@device_ns.route('/<int:device_id>/')
@device_ns.param('device_id', 'The device identifier')
class DeviceInformation(Resource):
    @device_ns.doc('fetch_device_information')
    @device_ns.doc(model=device_information_model)
    @device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
    def get(self, device_id):
        '''Fetch a Device Information and Configuration'''

        device = get_device(device_id)
        active_device_profile = get_active_profile(device)
        data = device.serialize()

        all_interfaces_of_device = get_all_interfaces(device)
        data['interfaces'] = [interface.serialize() for interface in all_interfaces_of_device]

        data['connections'] = [connection.serialize() for connection in active_device_profile.connections]

        return jsonify(data)

    @device_ns.doc('update_connection_config')
    @device_ns.expect(connection_list_model, validate=True)
    @device_ns.doc(model=connection_list_model)
    @device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
    @device_ns.response(400, '{"message": Bad Physical Interface Mapping in {<connection>}!"}')
    def put(self, device_id):
        '''Update Device Connection Configuration'''
        connections = connection_parser.parse_arguments()
        device = get_device(device_id)

        active_device_profile = get_active_profile(device)
        active_device_connections = active_device_profile.connections.copy()

        for connection in connections:
            connection_name = connection['connection_name']
            bandwidth_value = connection['bandwidth']
            delay_value = connection['delay']
            packet_loss_value = connection['packet_loss']
            jitter_value = connection['jitter']
            corruption_value = connection['corruption']
            duplication_value = connection['duplication']

            all_parameters = {
                'bandwidth': bandwidth_value,
                'delay': delay_value,
                'packet_loss': packet_loss_value,
                'jitter': jitter_value,
                'corruption': corruption_value,
                'duplication': duplication_value
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
                   and jitter_value == DEFAULT_JITTER and packet_loss_value == DEFAULT_PACKET_LOSS
                   and corruption_value == DEFAULT_CORRUPTION and duplication_value == DEFAULT_DUPLICATION):
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
                api.abort(400, str(e))

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
