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

# interface_parser = api.parser()
# interface_parser.add_argument(
#     'logical_name',
#     type=str,
#     help='logical name of interface (what will be shown in the UI)'
# )
# interface_parser.add_argument(
#     'physical_name',
#     type=str,
#     help='physical name which the interface has on the host (f.e ens123)'
# )
# interface_parser.add_argument(
#     'delay',
#     type=int,
#     help='delay of the interface'
# )


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
    'connection_id': fields.Integer,
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

connection_config_model = api.model('configuration_config_model', {
    'connection_name': fields.String,
    'interface1': fields.String,
    'interface2': fields.String,
    'delay': fields.Integer,
    'packet_loss': fields.Integer,
    'bandwidth': fields.Integer,
    'jitter': fields.Integer
})

device_information_model = api.model('configuration_model', {
    'active_profile_name': fields.String(attribute='active_profile.profile_name'),
    'device_id': fields.Integer,
    'device_name': fields.String,
    'management_ip': fields.String,
    'connections': fields.List(fields.Nested(connection_model)),
    'interfaces': fields.List(fields.Nested(interface_model)),
})
# interface_post_model = api.model('interface_post', {
#     'physical_name': fields.String(required=True),
#     'logical_name': fields.String
# })

# interface_put_model = api.model('interface_put', {
#     'logical_name': fields.String,
#     'physical_name': fields.String,
#     'delay': fields.Integer
# })


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
    def post(self):
        '''Create a new Device'''
        args = device_parser.parse_args()
        device_name = args['device_name']
        device_name_exists = DeviceModel.query.filter_by(device_name=device_name).first()
        if device_name_exists:
            api.abort(404, f"Host Name is already used!")
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
@device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
@device_ns.param('device_id', 'The device identifier')
class DeviceInformation(Resource):
    @device_ns.doc('fetch_device_information')
    @device_ns.doc(model=device_information_model)
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
    @device_ns.expect(connection_config_model, validate=True)
    @device_ns.doc(model=connection_list_model)
    def put(self, device_id):
        error_message = "Device or allocated Profile or Interface not found!"
        args = connection_config_parser.parse_args()
        connections = args['connections']

        device = DeviceModel.query.filter_by(device_id=device_id).first_or_404(description=error_message)
        active_device_profile = ProfileModel.query.filter_by(
            belongs_to_device=device).first_or_404(description=error_message)
        active_device_connections = active_device_profile.connections

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
            try:
                if active_connection is None:
                    physical_interface1_name = next(
                        interface.physical_name for interface in device.interfaces
                        if interface.has_logical_interface is logical_interface1)

                    physical_interface2_name = next(
                        interface.physical_name for interface in device.interfaces
                        if interface.has_logical_interface is logical_interface2)
                    connection_to_add = ConnectionModel(
                        connection['connection_name'],
                        logical_interface1.logical_interface_id,
                        logical_interface2.logical_interface_id,
                        active_device_profile.profile_id
                    )

                    db.session.add(connection_to_add)
                    db.session.commit()

                    print(salt_api.add_connection(
                        device.device_name,
                        connection['connection_name'],
                        physical_interface1_name,
                        physical_interface2_name
                    ))

                    bandwidth_value = connection['bandwidth']
                    delay_value = connection['delay']
                    packet_loss_value = connection['packet_loss']
                    jitter_value = connection['jitter']

                    if(bandwidth_value != 1000):
                        bandwidth_to_add = ParameterModel(
                            'bandwidth',
                            bandwidth_value,
                            connection_to_add.connection_id
                        )
                        db.session.add(bandwidth_to_add)
                        db.session.commit()
                        print(bandwidth_to_add)

                        # Todo implement and execute salt module
                        # salt_api.add_bandwidth(
                        # device.device_name,
                        # connection['connection_name'],
                        # connection['bandwidth']
                        # )

                    if(delay_value != 0):
                        delay_to_add = ParameterModel(
                            'delay',
                            delay_value,
                            connection_to_add.connection_id
                        )
                        db.session.add(delay_to_add)
                        db.session.commit()
                        print(delay_to_add)

                        # Todo implement and execute salt module
                        # salt_api.add_delay(
                        # device.device_name,
                        # connection['connection_name'],
                        # connection['delay']
                        # )

                    if(packet_loss_value != 0):
                        packet_loss_to_add = ParameterModel(
                            'packet_loss',
                            packet_loss_value,
                            connection_to_add.connection_id
                        )
                        db.session.add(packet_loss_to_add)
                        db.session.commit()
                        print(packet_loss_to_add)

                        # Todo implement and execute salt module
                        # salt_api.add_delay(
                        # device.device_name,
                        # connection['connection_name'],
                        # connection['delay']
                        # )

                    if(jitter_value != 0):
                        jitter_to_add = ParameterModel(
                            'jitter',
                            jitter_value,
                            connection_to_add.connection_id
                        )
                        db.session.add(jitter_to_add)
                        db.session.commit()
                        print(jitter_to_add)

                        # Todo implement and execute salt module
                        # salt_api.add_jitter(
                        # device.device_name,
                        # connection['connection_name'],
                        # connection['jitter']
                        # )

                else:
                    # Here we have to find the differences between the active connection
                    # and the connectipn configuration which has send within the PUT
                    
                    print('else matters!')
                    # print(connection)
                    # print(active_connection)
                    # todo change connections

                    # delete the current connection from active_device_connection
                    # neeed to check if a connection has to be deleted
                    # print(f"before removal: {active_device_connections}")
                    # active_device_connections.remove(active_connection)
                    # print(f"after removal: {active_device_connections}")

            except Exception:
                db.session.rollback()

        # Todo: Delete all connections which remain in active_device_connection
        # This are the connection which aren't mentioned in the sent configuration
        # and therefore have to be deleted

        return jsonify(connections=[connection.serialize() for connection in active_device_profile.connections])


@device_ns.route('/<int:device_id>/interfaces/')
@device_ns.response(404, '{"message": "Device or allocated Profile not found!"}')
@device_ns.param('device_id', 'The device identifier')
class InterfaceList(Resource):
    @device_ns.doc('fetch_interfaces')
    @device_ns.doc(model=interface_list_model)
    def get(self, device_id):
        '''Fetch all Interfaces of a specific Device'''
        all_interfaces_of_device = InterfaceModel.query.filter_by(belongs_to_device_id=device_id).all()
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

# {
#   "connections": [
    # {
    #   "connection": "Connection1",
    #   "connection_id": 1,
    #   "interface1": "LAN A",
    #   "interface2": "LAN B",
    #   "delay": 0,
    #   "packet_loss": 5,
    #   "bandwidth": 100,
    #   "jitter": 5
    # },
    # {
    #   "connection": "Connection2",
    #   "connection_id": 2,
    #   "interface1": "LAN C",
    #   "interface2": "LAN D",
    #   "delay": 0,
    #   "packet_loss": 5,
    #   "bandwidth": 100,
    #   "jitter": 5
    # }
#   ]
# }


# @device_ns.route('/<int:device_id>')
# @device_ns.response(404, '{"message": "Host not found"}')
# @device_ns.param('host_id', 'The host identifier')
# class HostById(Resource):
#     @device_ns.doc('get_host')
#     @device_ns.marshal_with(host_model)
#     def get(self, host_id):
#         '''Fetch information about a host given its identifier'''
#         return HostModel.query.filter_by(host_id=host_id).first_or_404()

#     @device_ns.doc('update_host')
#     @device_ns.expect(body=[host_put_model], validate=True)
#     @device_ns.marshal_with(host_model, code=200)
#     @device_ns.response(400, '{"message": "Missing required properties"}')
#     def put(self, host_id):
#         '''Update Host Information given its identifier'''
#         args = host_parser.parse_args()
#         host = HostModel.query.filter_by(host_id=host_id).first_or_404()
#         changed = False
#         if host.name is not args['name'] and args['name'] is not None:
#             host.name = args['name']
#             changed = True
#         if host.available is not args['available'] and args['available'] is not None:
#             host.available = args['available']
#             changed = True
#         if changed:
#             try:
#                 db.session.add(host)
#                 db.session.commit()
#             except Exception:
#                 db.session.rollback()
#         return host, 200

#     @device_ns.doc('delete_host')
#     @device_ns.response(204, '')
#     @device_ns.response(404, '{"message": "Host ID not found"}')
#     @device_ns.response(500, '{"message": "Failed to delete Host given its ID"}')
#     def delete(self, host_id):
#         '''Delete Host Information given its identifier'''
#         host = HostModel.query.filter_by(host_id=host_id).first_or_404()
#         if host:
#             try:
#                 db.session.delete(host)
#                 db.session.commit()
#             except Exception:
#                 db.session.rollback()
#                 api.abort(500, f"Failed to delete Host with {host_id}")
#             return '', 204
#         api.abort(404, f"Host with {host_id} not found")


# @device_ns.route('/<int:host_id>/interfaces/', '/<int:host_id>/interfaces')
# @device_ns.response(404, '{"message": "Host not found"}')
# @device_ns.param('host_id', 'The host identifier')
# class InterfaceList(Resource):
#     @device_ns.doc('list_interfaces')
#     @device_ns.marshal_list_with(interface_model)
#     def get(self, host_id):
#         '''Fetch all Interfaces of a specific hosts'''
#         return InterfaceModel.query.filter_by(host_id=host_id).all()

#     @device_ns.doc('create_interface')
#     @device_ns.expect(interface_post_model, validate=True)
#     @device_ns.marshal_with(interface_model, code=201)
#     @api.response(400, '{"message": "Missing required properties"}')
#     def post(self, host_id):
#         '''Create Interface given the host identifier'''
#         args = interface_parser.parse_args()
#         interface = InterfaceModel(
#             args['physical_name'],
#             host_id,
#             args['logical_name']
#         )
#         try:
#             db.session.add(interface)
#             db.session.commit()
#         except Exception:
#             db.session.rollback()
#         return interface, 201


# @device_ns.route(
#     '/<int:host_id>/interfaces/<int:int_id>/',
#     '/<int:host_id>/interfaces/<int:int_id>'
# )
# @device_ns.response(404, '{"message": "Host or Interface not found"}')
# @device_ns.param('host_id', 'The host identifier')
# @device_ns.param('int_id', 'The interface identifier')
# class IntById(Resource):
#     @device_ns.doc('get_interface')
#     @device_ns.marshal_with(interface_model)
#     def get(self, host_id, int_id):
#         '''Fetch information about a interface given host and its identifier'''
#         return InterfaceModel.query.filter_by(int_id=int_id).first_or_404()

#     @device_ns.doc('update_interface')
#     @device_ns.expect(interface_put_model, validate=True)
#     @device_ns.marshal_with(interface_model, code=200)
#     @device_ns.response(400, '{"message": "Missing required properties"}')
#     def put(self, host_id, int_id):
#         '''Update Interface Information given the host identifier'''
#         args = interface_parser.parse_args()
#         interface = InterfaceModel.query.filter_by(int_id=int_id).first_or_404()
#         changed = False
#         code = 400
#         if interface.logical_name is not args['logical_name'] and args['logical_name'] is not None:
#             interface.logical_name = args['logical_name']
#             changed = True
#         if interface.physical_name is not args['physical_name'] and args['physical_name'] is not None:
#             interface.physical_name = args['physical_name']
#             changed = True
#         if interface.delay is not args['delay'] and args['delay'] is not None:
#             if args['delay'] < 0:
#                 api.abort(412, f"{args['delay']} is not a positive value")
#             if args['delay'] == 0:
#                 code = salt_api.remove_delay(interface.physical_name)
#             else:
#                 code = salt_api.set_delay(interface.physical_name, args['delay'])
#             interface.delay = args['delay']
#             changed = True
#         if changed:
#             try:
#                 db.session.add(interface)
#                 db.session.commit()
#             except Exception:
#                 db.session.rollback()
#         return interface, code

#     @device_ns.doc('delete_interface')
#     @device_ns.response(204, '')
#     @device_ns.response(404, '{"message": "Host or Interface ID not found"}')
#     @device_ns.response(500, '{"message": "Failed to delete Interface with the given ID"}')
#     def delete(self, host_id, int_id):
#         '''Delete Interface given Host and its identifier'''
#         interface = InterfaceModel.query.filter_by(int_id=int_id).first_or_404()
#         if interface:
#             try:
#                 db.session.delete(interface)
#                 db.session.commit()
#             except Exception:
#                 db.session.rollback()
#                 api.abort(500, f"Failed to delete Interface with {host_id}")
#             return '', 204
#         api.abort(404, f"Interface with {int_id} not found")
