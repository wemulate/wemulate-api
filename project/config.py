import os


def configure_app(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if os.environ.get('WEMULATE_TESTING') == 'True':
        app.logger.debug('Using Wemulate Testing Configuration inclusive SQLLite DB and Mockup')
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
        app.config['SALT_MOCKUP'] = True
    else:
        app.config['SALT_MOCKUP'] = False
        app.logger.debug('Using Wemulate Real Live Configuration inclusive Postgres DB and Mockup')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{user}:{pw}@{url}/{db}'.format(
            user=os.environ.get('POSTGRES_USER'),
            pw=os.environ.get('POSTGRES_PASSWORD'),
            url='{}:{}'.format(
                os.environ.get('POSTGRES_HOST'),
                os.environ.get('POSTGRES_PORT')),
            db=os.environ.get('POSTGRES_DB')
        )
