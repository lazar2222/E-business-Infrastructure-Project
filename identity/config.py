import os
import datetime

DATABASE_URL = os.environ['DATABASE_URL']

class Config():
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:root@{DATABASE_URL}/identity'
    JWT_SECRET_KEY = 'JWT_SECRET_DEV_KEY'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours = 1)