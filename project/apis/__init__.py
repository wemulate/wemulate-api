from apis.salt import SaltApi
from mockup.salt_mockup import SaltMockup
import os


def create_salt_api():
    salt_url = os.environ.get('SALT_API')
    salt_password = os.environ.get('SALT_PASSWORD')
    salt_api = SaltApi(salt_url, 'salt', salt_password)
    return salt_api

def create_salt_mockup():
    salt_mockup = SaltMockup('url', 'salt', 'password')
    return salt_mockup
