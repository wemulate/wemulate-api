import json
from core import db

class ProfileModel(db.Model):
    __tablename__ = 'profile'
    profile_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    profile_name = db.Column(db.String(50))
    connections = db.relationship(
        'ConnectionModel',
        backref='profile',
        lazy=False,
        cascade='delete',
        order_by='asc(ConnectionModel.connection_name)'
    )

    def __init__(self, name):
        self.profile_name = name

    def __repr__(self):
        return json.dumps({
            'profile_id': self.profile_id,
            'profile_name': self.profile_name
        }
        )


class DeviceModel(db.Model):
    __tablename__ = 'device'
    device_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    device_name = db.Column(db.String(50), nullable=False)
    management_ip = db.Column(db.String(16), nullable=False)
    active_profile_id = db.Column(
        db.Integer,
        db.ForeignKey('profile.profile_id'),
        nullable=False
    )
    interfaces = db.relationship(
        'InterfaceModel',
        backref='device',
        lazy=False,
        cascade='delete',
        order_by='asc(InterfaceModel.interface_id)'
    )

    def __init__(self, device_name, profile_id, management_ip='127.0.0.1'):
        self.device_name = device_name
        self.management_ip = management_ip
        self.active_profile_id = profile_id

    def __repr__(self):
        return json.dumps({
            'device_id': self.device_id,
            'device_name': self.device_name,
            'management_ip': self.management_ip,
            'active_profile': self.active_profile.profile_name
        })


class InterfaceModel(db.Model):
    __tablename__ = 'interface'
    interface_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    physical_name = db.Column(db.String(50), nullable=False)
    belongs_to_device_id = db.Column(
        db.Integer,
        db.ForeignKey('device.device_id'),
        nullable=False
    )
    has_logical_interface_id: db.Column(
        db.Integer,
        db.ForeignKey('logical_interface.logical_interface_id'),
        nullable=True
    )
    interface_status = db.Column(db.Enum('up', 'down', name='interface_status_enum'), nullable=False, default='up')

    def __init__(self, physical_name, device_id, has_logical_interface_id=None):
        self.physical_name = physical_name
        self.belongs_to_device_id = device_id
        self.has_logical_interface_id = has_logical_interface_id

    def __repr__(self):
        if self.has_logical_interface_id is not None:
            return json.dumps({
                'interface_id': self.interface_id,
                'physical_name': self.physical_name,
                'has_logical_interface_id': self.has_logical_interface_id,
                'device_id': self.belongs_to_device_id,
                'status': self.interface_status
            })
        else:
            return json.dumps({
                'interface_id': self.interface_id,
                'physical_name': self.physical_name,
                'has_logical_interface_id': None,
                'device_id': self.belongs_to_device_id,
                'status': self.interface_status
            })


class LogicalInterfaceModel(db.Model):
    __tablename__ = 'logical_interface'
    logical_interface_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    logical_name = db.Column(db.String(50), nullable=False)

    def __init__(self, logical_name):
        self.logical_name = logical_name

    def __repr__(self):
        return json.dumps({
            'logical_interface_id': self.logical_interface_id,
            'logical_name': self.logical_name
        })


class ConnectionModel(db.Model):
    __tablename__ = 'connection'
    connection_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    connection_name = db.Column(db.String(50), nullable=False)
    bidirectional = db.Column(db.Boolean, default=True)
    first_logical_interface_id = db.Column(
        db.Integer,
        db.ForeignKey('logical_interface.logical_interface_id'),
        nullable=False
    )
    second_logical_interface_id = db.Column(
        db.Integer,
        db.ForeignKey('logical_interface.logical_interface_id'),
        nullable=False
    )
    belongs_to_profile_id = db.Column(
        db.Integer,
        db.ForeignKey('profile.profile_id'),
        nullable=False
    )
    parameters = db.relationship(
        'ParameterModel',
        backref='connection',
        lazy=False,
        cascade='delete',
        order_by='asc(ParameterModel.parameter_name)'
    )

    def __init__(self, connection_name, first_logical_interface_id,
                 second_logical_interface_id, profile_id, bidirectional=True):
        self.connection_name = connection_name
        self.first_logical_interface_id = first_logical_interface_id
        self.second_logical_interface_id = second_logical_interface_id
        self.belongs_to_profile_id = profile_id
        self.bidirectional = bidirectional

    def __repr__(self):
        return json.dumps({
            'connection_id': self.connection_id,
            'connection_name': self.connection_name,
            'bidirectional': self.bidirectional,
            'first_logical_interface_id': self.first_logical_interface_id,
            'second_logical_interface_id': self.second_logical_interface_id,
            'belongs_to_profile_id': self.belongs_to_profile_id
        })


class ParameterModel(db.Model):
    __tablename__ = 'parameter'
    parameter_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    parameter_name = db.Column(
        db.Enum('bandwith', 'delay', 'packer_loss', 'jitter', name='parameter_name_enum'), nullable=False
    )
    value = db.Column(db.Integer, nullable=False)
    belongs_to_connection_id = db.Column(
        db.Integer,
        db.ForeignKey('connection.connection_id'),
        nullable=False
    )
    active = db.Column(db.Boolean, default=True)
    has_on_off_timer_id = db.Column(
        db.Integer,
        db.ForeignKey('on_off_timer.on_off_timer_id'),
        nullable=True
    )

    def __init__(self, parameter_name, value, connection_id, on_off_timer_id=None):
        self.parameter_name = parameter_name
        self.value = value
        self.belongs_to_connection_id = connection_id
        self.active = True
        self.has_on_off_timer_id = on_off_timer_id

    def __repr__(self):
        return json.dumps({
            'parameter_id': self.parameter_id,
            'parameter_name': self.parameter_name,
            'value': self.value,
            'connection_id': self.belongs_to_connection_id,
            'active': self.active,
            'on_off_timer_id': self.has_on_off_timer_id
        })


class OnOffTimerModel(db.Model):
    __tablename__ = 'on_off_timer'
    on_off_timer_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    period = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def __init__(self, period, duration):
        self.period = period,
        self.duration = duration

    def __repr__(self):
        return json.dumps({
            'on_off_timer_id': self.on_off_timer_id,
            'period': self.period,
            'duration': self.duration
        })
