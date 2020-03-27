from apis.salt import SaltApi
import os


def create_salt_api():
    salt_url = os.environ.get('SALT_API')
    salt_password = os.environ.get('SALT_PASSWORD')
    salt_api = SaltApi(salt_url, 'salt', salt_password)
    return salt_api
