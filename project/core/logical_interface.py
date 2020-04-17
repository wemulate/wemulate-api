from core.models import LogicalInterfaceModel
import string
from core import db

ALPHABET = list(string.ascii_uppercase)

def create_logical_interfaces():
    for character in ALPHABET:
        logical_interface = LogicalInterfaceModel("LAN-" + character)
        try:
            db.session.add(logical_interface)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise(Exception)
