from core import api, app  # noqa: F401
from device_ns import device_ns

api.add_namespace(device_ns)
