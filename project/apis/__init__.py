from apis.salt import SaltApi


def create_salt_api():
    salt_api = SaltApi('http://localhost:8000', 'salt', 'EPJ@2020!!')
    return salt_api

