import os

from backend.app import create_app


config_name = os.environ.get('FLASK_CONFIG', 'dev')
app = create_app(config_name)
