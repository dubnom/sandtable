from pathlib import Path

from flask import Flask
from flask_socketio import SocketIO


PROJECT_ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__, template_folder=str(PROJECT_ROOT / 'views'))
socketio = SocketIO(app, cors_allowed_origins="*")
