from flask_restplus import Resource, fields
from core import db, create_app
from core.models import HostModel, InterfaceModel
from apis import create_salt_api
from localhost import create_localhost

app, api, host_ns = create_app()
salt_api = create_salt_api()

# Create localhost with all interfaces
# Just for demo and prototype
create_localhost()

# Parser and Models
host_parser = api.parser()
host_parser.add_argument(
    'name',
    type=str,
    help='hostname of the device/minion'
)
host_parser.add_argument(
    'physically',
    type=bool,
    help='define if device is physically or not'
)
host_parser.add_argument(
    'available',
    type=bool,
    help='define if device is available or not'
)

interface_parser = api.parser()
interface_parser.add_argument(
    'logical_name',
    type=str,
    help='logical name of interface (what will be shown in the UI)'
)
interface_parser.add_argument(
    'physical_name',
    type=str,
    help='physical name which the interface has on the host (f.e ens123)'
)
interface_parser.add_argument(
    'delay',
    type=int,
    help='delay of the interface'
)


host_model = api.model('host', {
    'host_id': fields.Integer,
    'name': fields.String,
    'physically': fields.Boolean,
    'available': fields.Boolean
})

host_post_model = api.model('host_post', {
    'name': fields.String(required=True),
    'physically': fields.Boolean
})

host_put_model = api.model('host_put', {
    'name': fields.String,
    'available': fields.Boolean
})

interface_model = api.model('interface', {
    'int_id': fields.Integer,
    'host_id': fields.Integer,
    'logical_name': fields.String,
    'physical_name': fields.String,
    'delay': fields.Integer
})

interface_post_model = api.model('interface_post', {
    'physical_name': fields.String(required=True),
    'logical_name': fields.String
})

interface_put_model = api.model('interface_put', {
    'logical_name': fields.String,
    'physical_name': fields.String,
    'delay': fields.Integer
})


@host_ns.route('/', '')
class HostList(Resource):
    @host_ns.doc('list_hosts')
    @host_ns.marshal_list_with(host_model)
    def get(self):
        '''Show all Hosts with related Information'''
        return HostModel.query.all()

    @host_ns.doc('create_host')
    @host_ns.expect(host_post_model, validate=True)
    @host_ns.marshal_with(host_model, code=201)
    @api.response(400, '{"message": "Missing required properties"}')
    def post(self):
        '''Create a new Host'''
        args = host_parser.parse_args()
        host = HostModel(args['name'], args['physically'])
        try:
            db.session.add(host)
            db.session.commit()
        except Exception:
            db.session.rollback()
        return host, 201


@host_ns.route('/<int:host_id>/', '/<int:host_id>')
@host_ns.response(404, '{"message": "Host not found"}')
@host_ns.param('host_id', 'The host identifier')
class HostById(Resource):
    @host_ns.doc('get_host')
    @host_ns.marshal_with(host_model)
    def get(self, host_id):
        '''Fetch information about a host given its identifier'''
        return HostModel.query.filter_by(host_id=host_id).first_or_404()

    @host_ns.doc('update_host')
    @host_ns.expect(body=[host_put_model], validate=True)
    @host_ns.marshal_with(host_model, code=200)
    @host_ns.response(400, '{"message": "Missing required properties"}')
    def put(self, host_id):
        '''Update Host Information given its identifier'''
        args = host_parser.parse_args()
        host = HostModel.query.filter_by(host_id=host_id).first_or_404()
        changed = False
        if host.name is not args['name'] and args['name'] is not None:
            host.name = args['name']
            changed = True
        if host.available is not args['available'] and args['available'] is not None:
            host.available = args['available']
            changed = True
        if changed:
            try:
                db.session.add(host)
                db.session.commit()
            except Exception:
                db.session.rollback()
        return host, 200

    @host_ns.doc('delete_host')
    @host_ns.response(204, '')
    @host_ns.response(404, '{"message": "Host ID not found"}')
    @host_ns.response(500, '{"message": "Failed to delete Host given its ID"}')
    def delete(self, host_id):
        '''Delete Host Information given its identifier'''
        host = HostModel.query.filter_by(host_id=host_id).first_or_404()
        if host:
            try:
                db.session.delete(host)
                db.session.commit()
            except Exception:
                db.session.rollback()
                api.abort(500, f"Failed to delete Host with {host_id}")
            return '', 204
        api.abort(404, f"Host with {host_id} not found")


@host_ns.route('/<int:host_id>/interfaces/', '/<int:host_id>/interfaces')
@host_ns.response(404, '{"message": "Host not found"}')
@host_ns.param('host_id', 'The host identifier')
class InterfaceList(Resource):
    @host_ns.doc('list_interfaces')
    @host_ns.marshal_list_with(interface_model)
    def get(self, host_id):
        '''Fetch all Interfaces of a specific hosts'''
        return InterfaceModel.query.filter_by(host_id=host_id).all()

    @host_ns.doc('create_interface')
    @host_ns.expect(interface_post_model, validate=True)
    @host_ns.marshal_with(interface_model, code=201)
    @api.response(400, '{"message": "Missing required properties"}')
    def post(self, host_id):
        '''Create Interface given the host identifier'''
        args = interface_parser.parse_args()
        interface = InterfaceModel(
            args['physical_name'],
            host_id,
            args['logical_name']
        )
        try:
            db.session.add(interface)
            db.session.commit()
        except Exception:
            db.session.rollback()
        return interface, 201


@host_ns.route(
    '/<int:host_id>/interfaces/<int:int_id>/',
    '/<int:host_id>/interfaces/<int:int_id>'
)
@host_ns.response(404, '{"message": "Host or Interface not found"}')
@host_ns.param('host_id', 'The host identifier')
@host_ns.param('int_id', 'The interface identifier')
class IntById(Resource):
    @host_ns.doc('get_interface')
    @host_ns.marshal_with(interface_model)
    def get(self, host_id, int_id):
        '''Fetch information about a interface given host and its identifier'''
        return InterfaceModel.query.filter_by(int_id=int_id).first_or_404()

    @host_ns.doc('update_interface')
    @host_ns.expect(interface_put_model, validate=True)
    @host_ns.marshal_with(interface_model, code=200)
    @host_ns.response(400, '{"message": "Missing required properties"}')
    def put(self, host_id, int_id):
        '''Update Interface Information given the host identifier'''
        args = interface_parser.parse_args()
        interface = InterfaceModel.query.filter_by(int_id=int_id).first_or_404()
        changed = False
        code = 400
        if interface.logical_name is not args['logical_name'] and args['logical_name'] is not None:
            interface.logical_name = args['logical_name']
            changed = True
        if interface.physical_name is not args['physical_name'] and args['physical_name'] is not None:
            interface.physical_name = args['physical_name']
            changed = True
        if interface.delay is not args['delay'] and args['delay'] is not None:
            if args['delay'] < 0:
                api.abort(412, f"{args['delay']} is not a positive value")
            if args['delay'] == 0:
                code = salt_api.remove_delay(interface.physical_name)
            else:
                code = salt_api.set_delay(interface.physical_name, args['delay'])
            interface.delay = args['delay']
            changed = True
        if changed:
            try:
                db.session.add(interface)
                db.session.commit()
            except Exception:
                db.session.rollback()
        return interface, code

    @host_ns.doc('delete_interface')
    @host_ns.response(204, '')
    @host_ns.response(404, '{"message": "Host or Interface ID not found"}')
    @host_ns.response(500, '{"message": "Failed to delete Interface with the given ID"}')
    def delete(self, host_id, int_id):
        '''Delete Interface given Host and its identifier'''
        interface = InterfaceModel.query.filter_by(int_id=int_id).first_or_404()
        if interface:
            try:
                db.session.delete(interface)
                db.session.commit()
            except Exception:
                db.session.rollback()
                api.abort(500, f"Failed to delete Interface with {host_id}")
            return '', 204
        api.abort(404, f"Interface with {int_id} not found")
