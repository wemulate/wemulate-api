from flask import Flask, request, jsonify
from flask_restplus import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
import netifaces
import os
from pepper import Pepper


app = Flask(__name__)
api = Api(app=app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interfaces.db'
db = SQLAlchemy(app)

# class hostname(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(50), unique=True, nullable=False)


@dataclass
class Interface(db.Model):
    id: int
    logical_name: str
    physical_name: str
    delay: int

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    logical_name = db.Column(db.String(50), unique=True)
    physical_name = db.Column(db.String(50), unique=True)
    delay = db.Column(db.Integer)


class SaltApi(object):
    def __init__(self):
        self.api = Pepper('http://localhost:8000')
        self.api.login('salt', 'EPJ@2020!!', 'sharedsecret')
    def execute(self, name, delay):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.set_delay', 'arg': [name, delay]}])

db.drop_all()
db.create_all()
db.session.commit()

salt_api = SaltApi()


for name in netifaces.interfaces():
    new_interface = Interface(physical_name=name)
    print(name)
    try:
        db.session.add(new_interface)
        db.session.commit()
    except Exception as e:
        print(f"Failed to create the interfaces entry for {name} in the DB - reason: {e}")
        db.session.rollback()
        db.session.close()


@api.route('/api/v1/interfaces/')
@api.route('/api/v1/interfaces')
class InterfaceList(Resource):
    def get(self):
        return jsonify((Interface.query.all()))
        """
        returns a list of available interfaces and related information
        """


@api.route('/api/v1/interfaces/<string:name>/')
@api.route('/api/v1/interfaces/<string:name>')
class FlaskInterface(Resource):
    def get(self, name):
        interface = Interface.query.filter_by(physical_name=name).first_or_404()
        return jsonify(interface)
        """
        returns information about specific interface
        """


@api.route('/api/v1/interfaces/<string:name>/delay/')
@api.route('/api/v1/interfaces/<string:name>/delay')
class Delay(Resource):
    def get(self, name):
        interface = Interface.query.filter_by(physical_name=name).first_or_404()
        return jsonify(interface.delay)
        """
        returns delay of specific interface
        """

    def put(self, name):
        
        interface = Interface.query.filter_by(physical_name=name).first_or_404()
        delay = request.form['value']
        return salt_api.execute(name, delay)
        # try:
        #     interface.delay = delay
        #     db.session.add(interface)
        #     db.session.commit()
        # except Exception as e:
        #     return(f"Failed to update the delay for the interface {name} in the DB - reason: {e}")
        #     db.session.rollback()
        # command = f"sudo tc qdisc add dev {name} root netem delay {delay}ms"
        # os.system(command)
        # return command

    def delete(self, name):
        interface = Interface.query.filter_by(physical_name=name).first_or_404()
        try:
            interface.delay = None
            db.session.add(interface)
            db.session.commit()
        except Exception as e:
            return(f"Failed to delete delay for the interface {name} in the DB - reason: {e}")
            db.session.rollback()
        command = f"sudo tc qdisc del dev {name} root netem delay 0"
        os.system(command)
        return command
