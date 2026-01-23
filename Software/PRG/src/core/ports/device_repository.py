"""
Device Repository Port
Definiert die Schnittstelle für Device-Persistierung
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..domain.device import Device, DeviceId


class DeviceRepository(ABC):
    """Port für Device-Persistierung"""
    
    @abstractmethod
    def find_by_id(self, device_id: DeviceId) -> Optional[Device]:
        """Finde Gerät nach ID"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Device]:
        """Finde alle Geräte"""
        pass
    
    @abstractmethod
    def find_active(self) -> List[Device]:
        """Finde alle aktiven Geräte"""
        pass
    
    @abstractmethod
    def find_due_for_inspection(self) -> List[Device]:
        """Finde Geräte, deren Inspektion fällig ist"""
        pass
    
    @abstractmethod
    def save(self, device: Device) -> None:
        """Speichere Gerät"""
        pass
    
    @abstractmethod
    def delete(self, device_id: DeviceId) -> None:
        """Lösche Gerät"""
        pass
    
    @abstractmethod
    def get_next_id(self) -> DeviceId:
        """Gebe nächste verfügbare Device ID zurück"""
        pass
