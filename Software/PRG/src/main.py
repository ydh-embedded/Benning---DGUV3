"""Benning Device Manager - Hexagonal Architecture Edition"""
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu BEVOR Module importiert werden
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from flask import Flask
from src.config.settings import get_config
from src.config.dependencies import container
from src.adapters.web.routes.device_routes import device_bp

def create_app():
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)
    app.register_blueprint(device_bp)

    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'ok'}, 200

    @app.route('/', methods=['GET'])
    def index():
        return {
            'name': 'Benning Device Manager',
            'version': '2.0.0',
            'architecture': 'Hexagonal',
            'status': 'running'
        }, 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
