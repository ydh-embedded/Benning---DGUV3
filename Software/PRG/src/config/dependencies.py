"""
Dependency Injection Container
"""
from ..core.ports.device_repository import DeviceRepository
from ..adapters.persistence.mysql_device_repository import MySQLDeviceRepository
from ..core.usecases.device_usecases import (
    GetDeviceUseCase,
    ListDevicesUseCase,
    CreateDeviceUseCase,
    GetDevicesDueForInspectionUseCase
)
from .settings import Settings


class DIContainer:
    """Dependency Injection Container"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._services = {}
    
    def get_device_repository(self) -> DeviceRepository:
        """Gebe Device Repository zurück"""
        if 'device_repository' not in self._services:
            db_config = self.settings.get_db_config()
            self._services['device_repository'] = MySQLDeviceRepository(db_config)
        return self._services['device_repository']
    
    def get_get_device_usecase(self) -> GetDeviceUseCase:
        """Gebe GetDevice Use Case zurück"""
        return GetDeviceUseCase(self.get_device_repository())
    
    def get_list_devices_usecase(self) -> ListDevicesUseCase:
        """Gebe ListDevices Use Case zurück"""
        return ListDevicesUseCase(self.get_device_repository())
    
    def get_create_device_usecase(self) -> CreateDeviceUseCase:
        """Gebe CreateDevice Use Case zurück"""
        return CreateDeviceUseCase(self.get_device_repository())
    
    def get_get_devices_due_usecase(self) -> GetDevicesDueForInspectionUseCase:
        """Gebe GetDevicesDueForInspection Use Case zurück"""
        return GetDevicesDueForInspectionUseCase(self.get_device_repository())
    
    def close(self):
        """Schließe alle Ressourcen"""
        if 'device_repository' in self._services:
            self._services['device_repository'].close()
