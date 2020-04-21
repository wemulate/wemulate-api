from flask_restplus import Resource, fields
from flask import jsonify
from core import db, create_app
from apis import create_salt_api
from core.models import ProfileModel, DeviceModel
from core.models import InterfaceModel, LogicalInterfaceModel
from core.models import ConnectionModel, ParameterModel
# , OnOffTimerModel
from core.logical_interface import create_logical_interfaces


app, api, device_ns = create_app()
salt_api = create_salt_api()
create_logical_interfaces()

# Parser

device_parser = api.parser()
device_parser.add_argument(
    'device_name',
    type=str,
    help='hostname of the device/minion'
)

device_parser.add_argument(
    'management_ip',
    type=str,
    help='define the management ip address (if not 127.0.0.1) of the device '
)

connection_config_parser = api.parser()
connection_config_parser.add_argument(
    'connections',
    type=list,
    location='json'
)

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


def parse_device_arguments():
    args = device_parser.parse_args()
    device_name = args['device_name']
    management_ip = args['management_ip']
    return device_name, management_ip


def device_exists(device_name):
    device_exists = DeviceModel.query.filter_by(device_name=device_name).first()
    return device_exists


def add_profile(device_name):
    profile_to_add = ProfileModel("default_" + device_name)
    db.session.add(profile_to_add)
    db.session.commit()
    return profile_to_add


def add_device(device_name, profile_id, management_ip):
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


def parse_connection_arguments():
    args = connection_config_parser.parse_args()
    return args['connections']


def get_all_interfaces(device):
    return InterfaceModel.query.filter_by(belongs_to_device_id=device.device_id).all()


def get_first_logical_interface(connection):
    return LogicalInterfaceModel.query.filter_by(logical_name=connection['interface1']).first()


def get_second_logical_interface(connection):
    return LogicalInterfaceModel.query.filter_by(logical_name=connection['interface2']).first()


def get_active_connection(logical_interface1, logical_interface2, active_device_connections):
    return next(
               (connection for connection in active_device_connections
                if connection.first_logical_interface is logical_interface1
                and connection.second_logical_interface is logical_interface2), None
    )


def get_first_physical_interface(device, logical_interface1):
    return next(
               (interface.physical_name for interface in device.interfaces
                if interface.has_logical_interface is logical_interface1), None
    )


def get_second_physical_interface(device, logical_interface2):
    return next(
               (interface.physical_name for interface in device.interfaces
                if interface.has_logical_interface is logical_interface2), None
    )


def add_connection(connection_name, logical_interface1, logical_interface2, active_device_profile):
    connection_to_add = ConnectionModel(
        connection_name,
        logical_interface1.logical_interface_id,
        logical_interface2.logical_interface_id,
        active_device_profile.profile_id
    )
    db.session.add(connection_to_add)
    db.session.commit()
    return connection_to_add


def add_all_parameters(all_parameters, connection, parameters, parameter_changed):
    for key, value in all_parameters.items():
        if(key == 'bandwidth'):
            add_parameter(
                'bandwidth',
                value,
                connection.connection_id
            )
            if(value != 1000):
                parameters['bandwidth'] = value

        if(key == 'delay'):
            add_parameter(
                'delay',
                value,
                connection.connection_id
            )
            if(value != 0):
                parameters['delay'] = value

        if(key == 'packet_loss'):
            add_parameter(
                'packet_loss',
                value,
                connection.connection_id
            )
            if(value != 0):
                parameters['packet_loss'] = value

        if(key == 'jitter'):
            add_parameter(
                'jitter',
                value,
                connection.connection_id
            )
            if(value != 0):
                parameters['jitter'] = value
    parameter_changed = True
    return parameter_changed


def add_parameter(parameter_name, value, connection_id):
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
    return parameter_changed
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
        device_name, management_ip = parse_device_arguments()
        if(device_exists(device_name)):
            api.abort(400, f"Device {device_name} is already used!")
        try:
            profile = add_profile(device_name)
            device = add_device(device_name, profile.profile_id, management_ip)
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
        connections = parse_connection_arguments()
        device = get_device(device_id)

        active_device_profile = get_active_profile(device,)
        active_device_connections = active_device_profile.connections.copy()

        for connection in connections:
            logical_interface1 = get_first_logical_interface(connection)
            logical_interface2 = get_second_logical_interface(connection)

            active_connection = get_active_connection(logical_interface1, logical_interface2, active_device_connections)

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

            physical_interface1_name = get_first_physical_interface(device, logical_interface1)

            physical_interface2_name = get_second_physical_interface(device, logical_interface2)

            if(physical_interface1_name is None or physical_interface2_name is None):
                raise Exception(f'Bad Physical Interface Mapping in {connection}!')

            try:
                if active_connection is None:
                    new_connection = add_connection(
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

                    parameter_changed = add_all_parameters(
                        all_parameters,
                        new_connection,
                        parameters_to_apply,
                        parameter_changed
                    )

                    db.session.commit()

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
                if parameter_changed and parameters_to_apply != {}:
                    interface_to_apply = get_first_physical_interface(device, logical_interface1)
                    salt_api.set_parameters(
                        device.device_name,
                        interface_to_apply,
                        parameters_to_apply
                    )

            except Exception as e:
                db.session.rollback()
                api.abort(400, str(e))

        for connection_to_delete in active_device_connections:
            db.session.delete(connection_to_delete)
            salt_api.remove_connection(
                device.device_name,
                connection_to_delete.connection_name
            )
            db.session.commit()

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
