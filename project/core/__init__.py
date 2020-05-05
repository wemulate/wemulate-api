from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from apis import create_salt_api, create_salt_mockup
from core.database.utils import DBUtils
from core.service import WemulateService


db = SQLAlchemy()
salt_api = create_salt_api()
wemulate_service = WemulateService(db, salt_api)

def create_app():
    global db, wemulate_service
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
        doc='/api/v1/'
    )

    return app, api

def create_app_test():
    global db, wemulate_service
    app = Flask(__name__)

    db = SQLAlchemy()
    db_settings = 'config.TestConfig'
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
        doc='/api/v1/'
    )

    salt_api = create_salt_mockup()  # mockup
    wemulate_service = WemulateService(db, salt_api)
    return app, api
