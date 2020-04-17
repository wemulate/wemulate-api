from core.models import LogicalInterfaceModel
import string
from core import db

def create_logical_interfaces():
    for character in list(string.ascii_uppercase):
        logical_interface = LogicalInterfaceModel("LAN-" + character)
        try:
            db.session.add(logical_interface)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise(Exception)
