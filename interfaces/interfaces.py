from flask import Flask, request
from flask_restplus import Api, Resource
from flask_sqlalchemy import SQLAlchemy
import json
import netifaces 
import os


app = Flask(__name__)
api = Api(app=app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interfaces.db'
db = SQLAlchemy(app)
db.create_all()

# class hostname(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(50), unique=True, nullable=False)

class Interface(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logical_name = db.Column(db.String(50), unique=True)
    physical_name = db.Column(db.String(50), unique=True)
    delay = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return '<Interface %r>' % self.id

# for name in netifaces.interfaces():
#     new_interface = Interface(id=counter, physical_name=name)
#     print(name)
#     print(new_interface)
#     counter += 1
#     try:
#         db.session.add(new_interface)
#         db.session.commit()
#     except:
#         print("Failed to create the interfaces entry in the DB")

# @api.route('/api/v1/interfaces/')
# class InterfaceList(Resource):
#     def get(self):
#         #interfaces  = netifaces.interfaces()
#         #return interfaces
#         return "test"
#         """
#         returns a list of available interfaces
#         """

# @api.route('/api/v1/interfaces/<string:name>/delay')
# class Interface(Resource):
#     def get(self, name):
#         command = f"tc qdisc show dev {name}"
#         value = os.popen(command).read()
#         return value
#         """
#         returns delay information about a specific interface
#         """
#     def put(self, name):
#         delay = request.form['value']
        

#         interface = Interface.query.get_or_404(id)
#         try:
#             command = f"sudo tc qdisc add dev {name} root netem delay {delay}ms"
#             db.session.add()
#         os.system(command)
#         return command
#     def delete(self, name):
#         command = f"sudo tc qdisc del dev {name} root netem delay 0"
#         os.system(command)
#         return "deleted"
 
        
      
