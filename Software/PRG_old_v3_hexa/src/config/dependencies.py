"""Dependency Injection Container"""
from src.config.settings import get_config
from src.adapters.persistence.mysql_device_repository import MySQLDeviceRepository
from src.core.usecases.device_usecases import (
    GetDeviceUseCase, ListDevicesUseCase, CreateDeviceUseCase,
    UpdateDeviceUseCase, DeleteDeviceUseCase
)

class Container:
    def __init__(self):
        self.config = get_config()
        self._init_repositories()
        self._init_usecases()

    def _init_repositories(self):
        db_config = {
            'host': self.config.DB_HOST,
            'port': self.config.DB_PORT,
            'user': self.config.DB_USER,
            'password': self.config.DB_PASSWORD,
            'database': self.config.DB_NAME
        }
        self.device_repository = MySQLDeviceRepository(db_config)

    def _init_usecases(self):
        self.get_device_usecase = GetDeviceUseCase(self.device_repository)
        self.list_devices_usecase = ListDevicesUseCase(self.device_repository)
        self.create_device_usecase = CreateDeviceUseCase(self.device_repository)
        self.update_device_usecase = UpdateDeviceUseCase(self.device_repository)
        self.delete_device_usecase = DeleteDeviceUseCase(self.device_repository)

container = Container()
