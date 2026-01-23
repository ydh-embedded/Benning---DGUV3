"""Device Repository Port"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.domain.device import Device

class DeviceRepository(ABC):
    """Abstract Device Repository"""

    @abstractmethod
    def get_by_id(self, device_id: int) -> Optional[Device]:
        pass

    @abstractmethod
    def get_all(self) -> List[Device]:
        pass

    @abstractmethod
    def create(self, device: Device) -> Device:
        pass

    @abstractmethod
    def update(self, device: Device) -> Device:
        pass

    @abstractmethod
    def delete(self, device_id: int) -> bool:
        pass

    @abstractmethod
    def get_by_serial(self, serial_number: str) -> Optional[Device]:
        pass
