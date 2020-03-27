import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pw}@{url}/{db}'.format(
        user=os.environ.get('POSTGRES_USER'),
        pw=os.environ.get('POSTGRES_PASSWORD'),
        url='{}:{}'.format(
            os.environ.get('POSTGRES_HOST'),
            os.environ.get('POSTGRES_PORT')),
        db=os.environ.get('POSTGRES_DB')
    )
