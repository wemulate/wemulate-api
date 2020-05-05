from flask_restplus import Resource, Namespace
from flask import jsonify
from apis import create_salt_api, create_salt_mockup
from core import db
from core.service import WemulateService
from api_parsers import ConnectionParser, DeviceParser
from api_models import connection_list_model, connection_model, device_information_model, \
    device_list_model, device_model, device_post_model, interface_list_model, interface_model


device_ns = Namespace('Device Operations', __name__, path='/v1/devices', doc='/api/v1/')

device_parser = DeviceParser(device_ns)
connection_parser = ConnectionParser(device_ns)
try:
    salt_api = create_salt_api()
except Exception as e:
    print('Error when creating salt api: ' + str(e.args))
    print('Using Mockup')
    salt_api = create_salt_mockup
wemulate_service = WemulateService(db, salt_api)


# Registering models in Namespace

device_ns.models[connection_list_model.name] = connection_list_model
device_ns.models[connection_model.name] = connection_model
device_ns.models[device_information_model.name] = device_information_model
device_ns.models[device_list_model.name] = device_list_model
device_ns.models[device_model.name] = device_model
device_ns.models[device_post_model.name] = device_post_model
device_ns.models[interface_list_model.name] = interface_list_model
device_ns.models[interface_model.name] = interface_model


# Routes

@device_ns.route('/')
class Device(Resource):
    @device_ns.doc('fetch_devices')
    @device_ns.doc(model=device_list_model)
    def get(self):
        '''Fetch a List of Devices with related Information'''
        try:
            devices = wemulate_service.get_device_list()
        except Exception as e:
            device_ns.abort(*(e.args))
        return jsonify(devices=devices)

    @device_ns.doc('create_device')
    @device_ns.expect(device_post_model, validate=True)
    @device_ns.marshal_with(device_model, code=201)
    @device_ns.response(400, '{"message": Device <device_name> is already in use!"}')
    def post(self):
        '''Create a new Device'''
        device_name, management_ip = device_parser.parse_arguments()
        try:
            device = wemulate_service.create_device(device_name, management_ip)
        except Exception as e:
            device_ns.abort(*(e.args))
        return device, 201


@device_ns.route('/<int:device_id>/')
@device_ns.param('device_id', 'The device identifier')
class DeviceInformation(Resource):
    @device_ns.doc('fetch_device_information')
    @device_ns.doc(model=device_information_model)
    @device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
    def get(self, device_id):
        '''Fetch a Device Information and Configuration'''
        try:
            device = wemulate_service.get_device(device_id)
        except Exception as e:
            device_ns.abort(*(e.args))
        return jsonify(device)

    @device_ns.doc('update_connection_config')
    @device_ns.expect(connection_list_model, validate=True)
    @device_ns.doc(model=connection_list_model)
    @device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
    @device_ns.response(400, '{"message": Bad Physical Interface Mapping in {<connection>}!"}')
    def put(self, device_id):
        '''Update Device Connection Configuration'''
        connections = connection_parser.parse_arguments()
        try:
            connection_list = wemulate_service.update_connection(device_id, connections)
        except Exception as e:
            device_ns.abort(*(e.args))
        return jsonify(connections=connection_list)


@device_ns.route('/<int:device_id>/interfaces/')
@device_ns.response(404, '{"message": Device or allocated Profile not found!"}')
@device_ns.param('device_id', 'The device identifier')
class InterfaceList(Resource):
    @device_ns.doc('fetch_interfaces')
    @device_ns.doc(model=interface_list_model)
    def get(self, device_id):
        '''Fetch all Interfaces of a specific Device'''
        try:
            device = wemulate_service.get_device(device_id)
            interfaces = wemulate_service.get_interface_list(device)
        except Exception as e:
            device_ns.abort(*(e.args))
        return jsonify(interfaces=interfaces)


@device_ns.route('/<int:device_id>/connections/')
@device_ns.response(404, '{"message": "Device not found"}')
@device_ns.param('device_id', 'The device identifier')
class ConnectionList(Resource):
    @device_ns.doc('fetch_connections')
    @device_ns.doc(model=connection_list_model)
    def get(self, device_id):
        '''Fetch all Connections of a specific Device'''
        try:
            device = wemulate_service.get_device(device_id)
            connections = wemulate_service.get_connection_list(device)
        except Exception as e:
            device_ns.abort(*(e.args))
        return jsonify(connections=connections)
