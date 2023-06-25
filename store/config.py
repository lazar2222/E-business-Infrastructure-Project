import os
import datetime

DATABASE_URL = os.environ['DATABASE_URL']

if not os.path.exists('private.key') or not os.path.exists('public.key'):
    private_key = None
    public_key = None
else:
    with open('private.key', 'r') as file:
        private_key = file.read()
    with open('public.key', 'r') as file:
        public_key = file.read()

class Config():
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:root@{DATABASE_URL}/store'
    JWT_SECRET_KEY = 'JWT_SECRET_DEV_KEY'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours = 1)
    USE_SPARK = os.environ['USE_SPARK'] == 'True' if 'USE_SPARK' in os.environ else False
    USE_ETH = os.environ['USE_ETH'] == 'True' if 'USE_ETH' in os.environ else False
    ETH_URL = os.environ['ETH_URL'] if 'ETH_URL' in os.environ else None
    OWNER_PRIVATE = private_key
    OWNER_PUBLIC = public_key