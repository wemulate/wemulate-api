from flask_restplus import fields, Model

# Models

device_model = Model('device_model', {
    'active_profile_name': fields.String(attribute='active_profile.profile_name'),
    'device_id': fields.Integer,
    'device_name': fields.String,
    'management_ip': fields.String,
})


device_list_model = Model('device_list_model', {
    'devices': fields.List(fields.Nested(device_model)),
})


device_post_model = Model('device_post_model', {
    'device_name': fields.String(required=True),
    'management_ip': fields.String
})

interface_model = Model('interface_model', {
    'interface_id': fields.Integer,
    'logical_name': fields.String(attribute='has_logical_interface.logical_name'),
    'physical_name': fields.String,
})


interface_list_model = Model('interface_list_model', {
    'interfaces': fields.List(fields.Nested(interface_model)),
})

connection_model = Model('connection_model', {
    'connection_name': fields.String,
    'corruption': fields.String,
    'duplication': fields.String,
    'interface1': fields.String,
    'interface2': fields.String,
    'delay': fields.Integer,
    'packet_loss': fields.Integer,
    'bandwidth': fields.Integer,
    'jitter': fields.Integer
})

connection_list_model = Model('connection_list_model', {
    'connections': fields.List(fields.Nested(connection_model)),
})

device_information_model = Model('device_information_model', {
    'active_profile_name': fields.String(attribute='active_profile.profile_name'),
    'device_id': fields.Integer,
    'device_name': fields.String,
    'management_ip': fields.String,
    'connections': fields.List(fields.Nested(connection_model)),
    'interfaces': fields.List(fields.Nested(interface_model)),
})
