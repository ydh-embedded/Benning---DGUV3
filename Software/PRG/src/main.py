"""
Benning Device Manager - Hexagonal Architecture
Main Application Entry Point
"""
from flask import Flask, render_template, jsonify
from config.settings import Settings
from config.dependencies import DIContainer
from adapters.web.routes.device_routes import DeviceRoutes, device_bp


def create_app(settings: Settings = None) -> Flask:
    """Factory für Flask-Anwendung"""
    
    if settings is None:
        settings = Settings()
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH
    
    # Dependency Injection
    di_container = DIContainer(settings)
    app.di_container = di_container
    
    # Routes registrieren
    device_routes = DeviceRoutes(
        get_device_uc=di_container.get_get_device_usecase(),
        list_devices_uc=di_container.get_list_devices_usecase(),
        create_device_uc=di_container.get_create_device_usecase(),
        get_due_uc=di_container.get_get_devices_due_usecase()
    )
    app.register_blueprint(device_bp)
    
    # Error Handler
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health Check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'version': settings.APP_VERSION})
    
    return app


if __name__ == '__main__':
    app = create_app()
    print(f"\n{'='*60}")
    print(f"🚀 {Settings.APP_NAME} v{Settings.APP_VERSION}")
    print(f"   Hexagonal Architecture Edition")
    print(f"   Running on http://0.0.0.0:5000")
    print(f"{'='*60}\n")
    app.run(host='0.0.0.0', port=5000, debug=Settings.FLASK_DEBUG)
