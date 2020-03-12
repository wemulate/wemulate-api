from flask import Flask
from flask_restplus import Api

app = Flask(__name__)
api = Api(app)

@api.route('/api/v1/interfaces')
class InterfaceList(Re)
