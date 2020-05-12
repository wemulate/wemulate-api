from flask_restplus import Resource, Namespace
from flask import jsonify
from api_parsers import ConnectionParser, DeviceParser
import core.service as wemulate_service
import api_models as models


device_ns = Namespace('Device Operations', __name__, path='/api/v1/devices', doc='/api/v1/')

device_parser = DeviceParser(device_ns)
connection_parser = ConnectionParser(device_ns)

# Registering models in Namespace

device_ns.models[models.connection_list_model.name] = models.connection_list_model
device_ns.models[models.connection_model.name] = models.connection_model
device_ns.models[models.device_information_model.name] = models.device_information_model
device_ns.models[models.device_list_model.name] = models.device_list_model
device_ns.models[models.device_model.name] = models.device_model
device_ns.models[models.device_post_model.name] = models.device_post_model
device_ns.models[models.interface_list_model.name] = models.interface_list_model
device_ns.models[models.interface_model.name] = models.interface_model


# Routes

@device_ns.route('/')
class Device(Resource):

    @device_ns.doc('fetch_devices')
    @device_ns.doc(model=models.device_list_model)
    @device_ns.response(500, '{"message": "Error when getting device list: <error>"}')
    def get(self):
        '''Fetch a List of Devices with related Information'''
        try:
            devices = wemulate_service.get_device_list()
        except Exception as e:
            device_ns.abort(*(e.args))
        return jsonify(devices=devices)

    @device_ns.doc('create_device')
    @device_ns.expect(models.device_post_model, validate=True)
    @device_ns.marshal_with(models.device_model, code=201)
    @device_ns.response(400, '{"message": "Device <device_name> is already in use!"}')
    @device_ns.response(500, '{"message": "Error when creating device: <error>"}')
    def post(self):
        '''Create a new Device'''
        device_name = device_parser.parse_arguments()
        try:
            device = wemulate_service.create_device(device_name)
        except Exception as e:
            device_ns.abort(*(e.args))
        return device, 201


@device_ns.route('/<int:device_id>/')
@device_ns.param('device_id', 'The device identifier')
class DeviceInformation(Resource):
    @device_ns.doc('fetch_device_information')
    @device_ns.doc(model=models.device_information_model)
    @device_ns.response(404, '{"message": "Device or allocated Profile not found!"}')
    @device_ns.response(500, '{"message": "Error when getting device: <error>"}')
    def get(self, device_id):
        '''Fetch a Device Information and Configuration'''
        try:
            device = wemulate_service.get_device(device_id)
        except Exception as e:
            device_ns.abort(*(e.args))
        return jsonify(device)

    @device_ns.doc('update_connection_config')
    @device_ns.expect(models.connection_list_model, validate=True)
    @device_ns.doc(model=models.connection_list_model)
    @device_ns.response(404, '{"message": "Device or allocated Profile not found!"}')
    @device_ns.response(500, '{"message": "Bad Physical Interface Mapping in <connection>!"}')
    @device_ns.response(500, '{"message": "Error when updating connection: <error>"}')
    def put(self, device_id):
        '''Update Device Connection Configuration'''
        connections = connection_parser.parse_arguments()
        try:
            connection_list = wemulate_service.update_connections(device_id, connections)
        except Exception as e:
            device_ns.abort(*(e.args))
        return jsonify(connections=connection_list)


@device_ns.route('/<int:device_id>/interfaces/')
@device_ns.response(404, '{"message": "Device or allocated profile not found!"}')
@device_ns.response(500, '{"message": "Error when getting interface list: <error>"}')
@device_ns.param('device_id', 'The device identifier')
class InterfaceList(Resource):
    @device_ns.doc('fetch_interfaces')
    @device_ns.doc(model=models.interface_list_model)
    def get(self, device_id):
        '''Fetch all Interfaces of a specific Device'''
        try:
            device = wemulate_service.get_device(device_id)
            interfaces = wemulate_service.get_interface_list(device)
        except Exception as e:
            device_ns.abort(*(e.args))
        return jsonify(interfaces=interfaces)


@device_ns.route('/<int:device_id>/connections/')
@device_ns.response(404, '{"message": "Device or allocated profile not found"}')
@device_ns.response(500, '{"message": "Error when getting connection list: <error>"}')
@device_ns.param('device_id', 'The device identifier')
class ConnectionList(Resource):
    @device_ns.doc('fetch_connections')
    @device_ns.doc(model=models.connection_list_model)
    def get(self, device_id):
        '''Fetch all Connections of a specific Device'''
        try:
            device = wemulate_service.get_device(device_id)
            connections = wemulate_service.get_connection_list(device)
        except Exception as e:
            device_ns.abort(*(e.args))
        return jsonify(connections=connections)
