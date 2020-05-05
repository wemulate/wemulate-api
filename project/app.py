from core import create_app
from device_ns import device_ns

app, api = create_app()

api.add_namespace(device_ns)
