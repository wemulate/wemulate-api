from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    db_settings = 'config.Config'
    app.config.from_object(db_settings)
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
        doc='/api/v1'
    )

    device_ns = api.namespace(
        'Device Operations',
        description='Execute all operations belonging to a wemulate device',
        path='/api/v1/devices'
    )
    # Not used yet
    # profile_ns = api.namespace(
    # 'Profile Operations',
    #  description='Profile Operations',
    #  path='/api/v1/profiles'
    # )

    return app, api, device_ns
