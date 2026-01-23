"""
Application Settings
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Anwendungs-Einstellungen"""
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3307'))
    DB_USER = os.getenv('DB_USER', 'benning')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'benning')
    DB_NAME = os.getenv('DB_NAME', 'benning_device_manager')
    DB_CHARSET = 'utf8mb4'
    DB_COLLATION = 'utf8mb4_unicode_ci'
    
    # File Storage
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Application
    APP_NAME = 'Benning Device Manager'
    APP_VERSION = '2.0.0'
    
    @classmethod
    def get_db_config(cls) -> dict:
        """Gebe Datenbank-Konfiguration zurück"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'charset': cls.DB_CHARSET,
            'collation': cls.DB_COLLATION
        }
