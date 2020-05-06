from apis.salt import SaltApi
from apis.salt_interface import SaltInterface
from mockup.salt_mockup import SaltMockup
import os

salt_api = SaltInterface()

def create_salt_api(app):
    salt_url = os.environ.get('SALT_API')
    salt_password = os.environ.get('SALT_PASSWORD')
    salt_api.init(app, salt_url, 'salt', salt_password)
    return salt_api
