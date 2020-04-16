from flask_restplus import Resource, fields
from flask import jsonify
import json
from core import db, create_app
from apis import create_salt_api
from core.models import ProfileModel, DeviceModel
# Not needed for device creation:
# InterfaceModel, LogicalInterfaceModel
# from core.models import ConnectionModel, ParameterModel, OnOffTimerModel


app, api, device_ns = create_app()
salt_api = create_salt_api()


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


device_model = api.model('device_get', {
    'active_profile_name': fields.String(attribute='active_profile.profile_name'),
    'device_id': fields.Integer,
    'device_name': fields.String,
    'management_ip': fields.String,
})


device_list_model = api.model('device_list', {
    'devices': fields.List(fields.Nested(device_model)),
})


device_post_model = api.model('device_post', {
    'device_name': fields.String(required=True),
    'management_ip': fields.String
})


# interface_model = api.model('interface', {
#     'int_id': fields.Integer,
#     'host_id': fields.Integer,
#     'logical_name': fields.String,
#     'physical_name': fields.String,
#     'delay': fields.Integer
# })

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
class HostList(Resource):
    @device_ns.doc('list_devices')
    @device_ns.doc(model=device_list_model)
    def get(self):
        '''Show all Devices with related Information'''
        resource_fields = {'devices': {fields.List(fields.Nested(device_model))}}
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
        except Exception:
            db.session.rollback()
        return device, 201


# @device_ns.route('/<int:host_id>/', '/<int:host_id>')
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
