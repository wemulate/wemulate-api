from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    db_settings = 'config.Config'
    app.config.from_object(db_settings)
    db.init_app(app)
    app.app_context().push()
    db.drop_all()  # Used for Test Purposes
    db.create_all()

    api = Api(
        app,
        version='1.0',
        title='WEmulate API',
        description='REST API for WEmulate ',
    )

    host_ns = api.namespace(
        'Host and Interface Operations',
        description='CRUD Hosts and Interfaces',
        path='/api/v1/hosts'
    )
    # Not used yet
    # profile_ns = api.namespace(
    # 'Profile Operations',
    #  description='Profile Operations',
    #  path='/api/v1/profiles'
    # )

    return app, api, host_ns
