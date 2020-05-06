from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from apis import create_salt_api
from config import configure_app
from mockup.salt_mockup import SaltMockup

db = SQLAlchemy()
try:
    salt_api = create_salt_api()
except Exception as e:
    salt_api = None
    print('Error setting up salt api: ' + str(e.args))

def create_app():
    global salt_api
    app = Flask(__name__)

    configure_app(app)
    db.init_app(app)
    app.app_context().push()
    db.drop_all()  # Used for Test Purposes
    db.create_all()
    CORS(app)

    api = Api(
        app,
        version='1.0',
        title='WEmulate API',
        description='REST API for WEmulate ',
        doc='/api/v1/'
    )

    if app.config['SALT_MOCKUP']:
        salt_api = SaltMockup('url', 'salt', 'password')

    return app, api
