from core import create_app  # noqa: F401
from device_ns import device_ns

app, api = create_app()
api.add_namespace(device_ns)
