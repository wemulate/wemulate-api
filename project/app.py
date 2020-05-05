from core import create_app, create_app_test
from device_ns import device_ns

app, api = create_app_test()
api.add_namespace(device_ns)
