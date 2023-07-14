import os
"""config for database"""
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'postgres')
DB_PORT = os.environ.get('DB_PORT', default=5432)
postgre_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
print(postgre_url)

"""config for emails"""
EMAIL_DOMEN_NAME = os.environ.get('EMAIL_DOMEN_NAME')
EMAIL_PORT = os.environ.get('EMAIL_PORT', default=587)
EMAIL_LOGIN = os.environ.get('EMAIL_NAME')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')


"""config for JWT credentials"""
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

reservation_time = 60 * 60
