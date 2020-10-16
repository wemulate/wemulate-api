from flask import Flask
from flask_restplus import Api
from flask_cors import CORS
from apis import create_salt_api
from core.database import db
import core.database.utils as dbutils
from config import configure_app
from mockup.salt_mockup import SaltMockup
import logging

def create_app():
    app = Flask(__name__)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    
    app.logger.info("BEGIN configuring app")
    configure_app(app)
    app.logger.info("FINISH configuring app")
    app.logger.info("BEGIN INIT DB")
    db.init_app(app)
    app.logger.info("FINISH INIT DB")
    app.app_context().push()
    app.logger.info("CREATE DB TABLES")
    db.create_all()
    app.logger.info("FINISH DB TABLES")


    # Create logical interfaces if not exist
    if not len(dbutils.get_logical_interface_list()):
        app.logger.info("Create logical Interfaces")
        dbutils.create_logical_interfaces()
        db.session.commit()
    
    # Delete Connection if exists after restart
    if len(dbutils.get_connection_list()):
        app.logger.info("Create logical Interfaces")
        dbutils.delete_present_connection()

    CORS(app)

    api = Api(
        app,
        version='1.0',
        title='WEmulate API',
        description='REST API for WEmulate ',
        doc='/api/v1/'
    )

    # Salt
    create_salt_api(app)

    return app, api
