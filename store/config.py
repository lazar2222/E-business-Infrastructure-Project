import os
import datetime

DATABASE_URL = os.environ['DATABASE_URL']

class Config():
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:root@{DATABASE_URL}/store'
    JWT_SECRET_KEY = 'JWT_SECRET_DEV_KEY'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours = 1)
    USE_SPARK = os.environ['USE_SPARK'] == 'True' if 'USE_SPARK' in os.environ else False
    USE_ETH = os.environ['USE_ETH'] == 'True' if 'USE_ETH' in os.environ else False