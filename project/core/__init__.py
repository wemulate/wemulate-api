from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Todo: If necessary run gunnicorn automatically
def create_app():
    app = Flask(__name__)
    db_settings = 'config.Config'
    app.config.from_object(db_settings)
    db.init_app(app)
    app.app_context().push()
    db.drop_all() # Used for Test Purposes
    db.create_all()
    
    api = Api(
        app,
        version='1.0',
        title='WEmulate API',
        description='REST API for WEmulate ',
    )

    host_ns = api.namespace('Host and Interface Operations', description='CRUD Hosts and Interfaces', path='/api/v1/hosts')
    #Not used yet
    #profile_ns = api.namespace('Profile Operations', description='Profile Operations', path='/api/v1/profiles') 
    
    # Create localhost and interfaces of it for test purposes
    create_localhost()

    return app, api, host_ns


from core.models import HostModel, InterfaceModel
import netifaces

def create_localhost():
    #Add localhost by starting appliction --> therefore localhost has always host_id = 1
    localhost = models.HostModel(name='localhost', physically=False)
    try:
        db.session.add(localhost)
        db.session.commit()
    except Exception as e:
        print(f'Failed to add localhost --> {e}')


    for name in netifaces.interfaces():
        new_interface = models.InterfaceModel(name, 1) #localhost has always host_id = 1
        print(name)
        try:
            db.session.add(new_interface)
            db.session.commit()
        except Exception as e:
            print(f"Failed to create the interfaces entry for {name} in the DB - reason: {e}")
            db.session.rollback()
            db.session.close()
    