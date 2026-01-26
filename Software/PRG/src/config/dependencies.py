"""Dependency Injection Container - Hexagonal Architecture"""
import os
from threading import Lock
from src.adapters.persistence.mysql_device_repository import MySQLDeviceRepository
from src.core.usecases.device_usecases import (
    CreateDeviceUseCase,
    ListDevicesUseCase,
    GetDeviceUseCase,
    UpdateDeviceUseCase,
    DeleteDeviceUseCase
)
from src.adapters.services.logger_service import LoggerService


class Container:
    """Dependency Injection Container for all use cases and repositories"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Container, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Nur einmal initialisieren (Singleton Pattern)
        if self._initialized:
            return
        
        self.logger = LoggerService()
        self._init_repositories()
        self._init_usecases()
        self._initialized = True
    
    def _init_repositories(self):
        """Initialize all repositories"""
        # Get database configuration from environment variables
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '3306'))
        db_user = os.getenv('DB_USER', 'benning_user')
        db_password = os.getenv('DB_PASSWORD', 'benning_password')
        db_name = os.getenv('DB_NAME', 'benning_db')
        
        self.logger.info(
            "Initializing repositories",
            db_host=db_host,
            db_port=db_port,
            db_name=db_name
        )
        
        # Initialize MySQL Device Repository with database credentials
        self.device_repository = MySQLDeviceRepository(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
    
    def _init_usecases(self):
        """Initialize all use cases"""
        self.logger.info("Initializing use cases")
        
        # Device Use Cases
        self.create_device_usecase = CreateDeviceUseCase(self.device_repository)
        self.list_devices_usecase = ListDevicesUseCase(self.device_repository)
        self.get_device_usecase = GetDeviceUseCase(self.device_repository)
        self.update_device_usecase = UpdateDeviceUseCase(self.device_repository)
        self.delete_device_usecase = DeleteDeviceUseCase(self.device_repository)
        
        self.logger.info("All use cases initialized successfully")

        # In der dependencies.py Datei sollte folgende Zeile existieren:
        self.container.create_device_usecase = CreateDeviceUseCase(self.container.device_repository)

# Create singleton container instance (nur einmal!)
container = Container()
