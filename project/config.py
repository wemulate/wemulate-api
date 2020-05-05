import os


def configure_app(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if app.config['TESTING']:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
        app.config['SALT_MOCKUP'] = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{user}:{pw}@{url}/{db}'.format(
            user=os.environ.get('POSTGRES_USER'),
            pw=os.environ.get('POSTGRES_PASSWORD'),
            url='{}:{}'.format(
                os.environ.get('POSTGRES_HOST'),
                os.environ.get('POSTGRES_PORT')),
            db=os.environ.get('POSTGRES_DB')
        )
