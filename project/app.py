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

# Parser and Models
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

device_information_model = api.model('configuration_model', {
    'active_profile_name': fields.String(attribute='active_profile.profile_name'),
    'device_id': fields.Integer,
    'device_name': fields.String,
    'management_ip': fields.String,
    'connections': fields.List(fields.Nested(connection_model)),
    'interfaces': fields.List(fields.Nested(interface_model)),
})

# Helper Functions

def add_parameter(parameter_name, value, connection_id):
    parameter_to_add = ParameterModel(
        parameter_name,
        value,
        connection_id
    )
    db.session.add(parameter_to_add)

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
    @device_ns.response(400, '{"message": Device Name <device_name> is already in use!"}')
    def post(self):
        '''Create a new Device'''
        args = device_parser.parse_args()
        device_name = args['device_name']
        device_name_exists = DeviceModel.query.filter_by(device_name=device_name).first()
        if device_name_exists:
            api.abort(400, f"Device Name {device_name} is already used!")
        management_ip = args['management_ip']
        profile = ProfileModel("default_" + device_name)
        try:
            db.session.add(profile)
            db.session.commit()
            if(management_ip is None):
                device = DeviceModel(device_name, profile.profile_id)
            else:
                device = DeviceModel(device_name, profile.profile_id, management_ip)
            db.session.add(device)
            db.session.commit()

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
        error_message = "Device or allocated Profile not found!"

        device = DeviceModel.query.filter_by(device_id=device_id).first_or_404(description=error_message)
        data = device.serialize()

        all_interfaces_of_device = InterfaceModel.query.filter_by(belongs_to_device_id=device_id).all()
        data['interfaces'] = [interface.serialize() for interface in all_interfaces_of_device]

        active_device_profile = \
            ProfileModel.query.filter_by(belongs_to_device=device).first_or_404(description=error_message)
        data['connections'] = [connection.serialize() for connection in active_device_profile.connections]
        return jsonify(data)

    @device_ns.doc('update_connection_config')
    @device_ns.expect(connection_list_model, validate=True)
    @device_ns.doc(model=connection_list_model)
    @device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
    @device_ns.response(400, '{"message": Bad Physical Interface Mapping in {<connection>}!"}')
    def put(self, device_id):
        '''Update Device Connection Configuration'''
        error_message = "Device or allocated Profile not found!"
        args = connection_config_parser.parse_args()
        connections = args['connections']

        device = DeviceModel.query.filter_by(device_id=device_id).first_or_404(description=error_message)
        active_device_profile = ProfileModel.query.filter_by(
            belongs_to_device=device).first_or_404(description=error_message)
        active_device_connections = active_device_profile.connections.copy()

        for connection in connections:
            logical_interface1 = LogicalInterfaceModel.query\
                .filter_by(logical_name=connection['interface1']).first()

            logical_interface2 = LogicalInterfaceModel.query\
                .filter_by(logical_name=connection['interface2']).first()
            active_connection = next(
                (connection for connection in active_device_connections
                 if connection.first_logical_interface is logical_interface1
                 and connection.second_logical_interface is logical_interface2),
                None
            )

            bandwidth_value = connection['bandwidth']
            delay_value = connection['delay']
            packet_loss_value = connection['packet_loss']
            jitter_value = connection['jitter']

            try:
                if active_connection is None:
                    physical_interface1_name = next(
                        (interface.physical_name for interface in device.interfaces
                         if interface.has_logical_interface is logical_interface1), None)

                    physical_interface2_name = next(
                        (interface.physical_name for interface in device.interfaces
                         if interface.has_logical_interface is logical_interface2), None)

                    if(physical_interface1_name is None or physical_interface2_name is None):
                        raise Exception(f'Bad Physical Interface Mapping in {connection}!')
                    connection_to_add = ConnectionModel(
                        connection['connection_name'],
                        logical_interface1.logical_interface_id,
                        logical_interface2.logical_interface_id,
                        active_device_profile.profile_id
                    )

                    db.session.add(connection_to_add)
                    db.session.commit()

                    salt_api.add_connection(
                        device.device_name,
                        connection['connection_name'],
                        physical_interface1_name,
                        physical_interface2_name
                    )

                    if(bandwidth_value != 1000):
                        add_parameter(
                            'bandwidth',
                            bandwidth_value,
                            connection_to_add.connection_id
                        )

                    if(delay_value != 0):
                        add_parameter(
                            'delay',
                            delay_value,
                            connection_to_add.connection_id
                        )

                    if(packet_loss_value != 0):
                        add_parameter(
                            'packet_loss',
                            packet_loss_value,
                            connection_to_add.connection_id
                        )

                    if(jitter_value != 0):
                        add_parameter(
                            'jitter',
                            jitter_value,
                            connection_to_add.connection_id
                        )

                    db.session.commit()

                    # Todo: execute salt module
                    # salt_api.add_jitter(
                    # device.device_name,
                    # connection['connection_name'],
                    # connection['jitter']
                    # )

                else:
                    if(connection['connection_name'] != active_connection.connection_name):
                        salt_api.remove_connection(
                            device.device_name,
                            active_connection.connection_name
                        )

                        salt_api.add_connection(
                            device.device_name,
                            connection['connection_name'],
                        )
                        active_connection.connection_name = connection['connection_name']

                    actual_bandwidth = next(
                        (parameter.value for parameter in active_connection.parameters
                            if parameter.parameter_name == 'bandwidth'),
                        1000
                    )
                    if(bandwidth_value != actual_bandwidth):
                        if(actual_bandwidth == 1000):
                            add_parameter(
                                'bandwidth',
                                bandwidth_value,
                                active_connection.connection_id
                            )
                        else:
                            actual_bandwidth.value = bandwidth_value
                            db.session.add(actual_bandwidth)

                    actual_delay = next(
                        (parameter.value for parameter in active_connection.parameters
                            if parameter.parameter_name == 'delay'),
                        0
                    )
                    if(delay_value != actual_delay):
                        if(actual_delay == 0):
                            add_parameter(
                                'delay',
                                delay_value,
                                active_connection.connection_id
                            )
                        else:
                            actual_delay.value = delay_value
                            db.session.add(actual_delay)

                    actual_jitter = next(
                        (parameter.value for parameter in active_connection.parameters
                            if parameter.parameter_name == 'jitter'),
                        0
                    )
                    if(jitter_value != actual_jitter):
                        if(actual_jitter == 0):
                            add_parameter(
                                'jitter',
                                jitter_value,
                                active_connection.connection_id
                            )
                        else:
                            actual_jitter.value = jitter_value
                            db.session.add(actual_jitter)

                    actual_packet_loss = next(
                        (parameter.value for parameter in active_connection.parameters
                            if parameter.parameter_name == 'packet_loss'),
                        0
                    )
                    if(packet_loss_value != actual_packet_loss):
                        if(actual_packet_loss == 0):
                            add_parameter(
                                'packet_loss',
                                packet_loss_value,
                                active_connection.connection_id
                            )
                        else:
                            actual_packet_loss.value = packet_loss_value
                            db.session.add(actual_packet_loss)
                    db.session.commit()
                    active_device_connections.remove(active_connection)
            except Exception as e:
                db.session.rollback()
                api.abort(400, str(e))

        # Todo: Delete all connections which remain in active_device_connection
        # This are the connection which aren't mentioned in the sent configuration
        # and therefore have to be deleted
        for connection_to_delete in active_device_connections:
            db.session.delete(connection_to_delete)
            salt_api.remove_connection(
                device.device_name,
                active_connection.connection_name
            )

        return jsonify(connections=[connection.serialize() for connection in active_device_profile.connections])


@device_ns.route('/<int:device_id>/interfaces/')
@device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
@device_ns.param('device_id', 'The device identifier')
class InterfaceList(Resource):
    @device_ns.doc('fetch_interfaces')
    @device_ns.doc(model=interface_list_model)
    def get(self, device_id):
        '''Fetch all Interfaces of a specific Device'''
        error_message = "Device or allocated Profile not found!"
        device = DeviceModel.query.filter_by(device_id=device_id).first_or_404(description=error_message)

        all_interfaces_of_device = InterfaceModel.query.filter_by(belongs_to_device_id=device.device_id).all()
        return jsonify(interfaces=[interface.serialize() for interface in all_interfaces_of_device])

@device_ns.route('/<int:device_id>/connections/')
@device_ns.response(404, '{"message": "Device not found"}')
@device_ns.param('device_id', 'The device identifier')
class ConnectionList(Resource):
    @device_ns.doc('fetch_connections')
    @device_ns.doc(model=connection_list_model)
    def get(self, device_id):
        '''Fetch all Connections of a specific Device'''
        error_message = "Device or allocated Profile not found!"
        device = DeviceModel.query.filter_by(device_id=device_id).first_or_404(description=error_message)

        active_device_profile = \
            ProfileModel.query.filter_by(belongs_to_device=device).first_or_404(description=error_message)

        return jsonify(connections=[connection.serialize() for connection in active_device_profile.connections])
