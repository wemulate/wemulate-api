from core import db
from json import dumps

class HostModel(db.Model):
    __tablename__ = 'host'
    host_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    name = db.Column(db.String(50), nullable=False)
    physically = db.Column(db.Boolean, default=False)
    available = db.Column(db.Boolean, default=True)
    interfaces = db.relationship(
        'InterfaceModel',
        backref='host',
        lazy=False,
        cascade='delete',
        order_by='asc(InterfaceModel.int_id)')

    def __init__(self, name, physically):
        self.name = name
        if physically is not None:
            self.physically = physically

    def __repr__(self):
        return json.dumps({
            'host_id': self.host_id,
            'name': self.name,
            'physically': self.physically,
            'available': self.available
        })


class InterfaceModel(db.Model):
    __tablename__ = 'interface'
    int_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True)
    logical_name = db.Column(db.String(50))
    physical_name = db.Column(db.String(50), nullable=False)
    delay = db.Column(db.Integer, default=0)
    host_id = db.Column(db.Integer, db.ForeignKey('host.host_id'), nullable=False)
    
    def __init__(self, physical_name,host_id, logical_name=None):
        self.physical_name = physical_name
        if not logical_name:
            self.logical_name = self.physical_name
        else:
            self.logical_name = logical_name
        self.host_id = host_id
    def __repr__(self):
        return json.dumps({
            'int_id': self.id,
            'logical_name': self.logical_name,
            'physical_name': self.physical_name,
            'delay': self.delay,
            'host_id': self.host_id
        })