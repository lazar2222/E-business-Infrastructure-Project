import sys
import time
import shutil
import os
from flask import Flask
from flask_migrate import Migrate, init, migrate,upgrade
from sqlalchemy_utils import database_exists, create_database

from config import Config

from models import database

application = Flask(__name__)
application.config.from_object(Config)

migration = Migrate(application, database)

while(True):
    try:
        if not database_exists(Config.SQLALCHEMY_DATABASE_URI):
            create_database(Config.SQLALCHEMY_DATABASE_URI)

        database.init_app(application)

        with application.app_context() as context:
            print('Init')
            init()
            print('Migrate')
            migrate(message=f'Production migration at {time.time()}')
            print('Upgrade')
            upgrade()

            print('Done')

            sys.exit(0)
    except Exception as ex:
        print('Waiting')
        #print(ex)
        #if os.path.exists('migrations'):
            #shutil.rmtree('migrations')
        time.sleep(1)
