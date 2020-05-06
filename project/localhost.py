import netifaces
from core.database import db
from core.models import HostModel, InterfaceModel


def create_localhost():
    # Add localhost by starting appliction therefore localhost has always host_id = 1
    localhost = HostModel(name='localhost', physically=False)
    try:
        db.session.add(localhost)
        db.session.commit()
    except Exception as e:
        print(f'Failed to add localhost --> {e}')

    for name in netifaces.interfaces():
        # localhost has always host_id = 1
        new_interface = InterfaceModel(name, 1)
        print(name)
        try:
            db.session.add(new_interface)
            db.session.commit()
        except Exception as e:
            print(f"Failed to create the interfaces entry for {name} in the DB - reason: {e}")
            db.session.rollback()
            db.session.close()
