import os
from dotenv import load_dotenv

load_dotenv()


def _build_db_uri():
    host     = os.environ.get('MYSQL_HOST',     'localhost')
    port     = os.environ.get('MYSQL_PORT',     '3306')
    user     = os.environ.get('MYSQL_USER',     'root')
    password = os.environ.get('MYSQL_PASSWORD', '')
    database = os.environ.get('MYSQL_DATABASE', 'cafeteria_db')
    return f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    SQLALCHEMY_DATABASE_URI = _build_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SSL — only active when MYSQL_SSL_CA env var is set (required by Aiven, skipped for local dev)
    _ssl_ca = os.environ.get('MYSQL_SSL_CA')
    if _ssl_ca:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {
                'ssl': {'ca': _ssl_ca}
            }
        }
