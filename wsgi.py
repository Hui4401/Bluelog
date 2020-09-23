import os
from dotenv import load_dotenv

from bluelog import create_app


flaskenv_path = os.path.join(os.path.dirname(__file__), '.flaskenv')
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(flaskenv_path):
    load_dotenv(flaskenv_path)
if os.path.exists(env_path):
    load_dotenv(env_path)

app = create_app()