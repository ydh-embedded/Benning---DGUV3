"""
Device Use Cases
Geschäftslogik für Geräteverwaltung
"""
from typing import List, Optional
from ..domain.device import Device, DeviceId
from ..ports.device_repository import DeviceRepository


class GetDeviceUseCase:
    """Use Case: Gerät abrufen"""
    
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository
    
    def execute(self, device_id: str) -> Device:
        device = self.device_repository.find_by_id(DeviceId(device_id))
        if not device:
            raise ValueError(f"Gerät {device_id} nicht gefunden")
        return device


class ListDevicesUseCase:
    """Use Case: Alle Geräte auflisten"""
    
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository
    
    def execute(self) -> List[Device]:
        return self.device_repository.find_all()


class ListActiveDevicesUseCase:
    """Use Case: Aktive Geräte auflisten"""
    
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository
    
    def execute(self) -> List[Device]:
        return self.device_repository.find_active()


class CreateDeviceUseCase:
    """Use Case: Neues Gerät erstellen"""
    
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository
    
    def execute(self, device_data: dict) -> Device:
        # Generiere nächste ID
        next_id = self.device_repository.get_next_id()
        
        # Erstelle Device
        device = Device(
            id=next_id,
            name=device_data['name'],
            type=device_data['type'],
            location=device_data['location'],
            manufacturer=device_data.get('manufacturer', ''),
            serial_number=device_data.get('serial_number', ''),
            purchase_date=device_data.get('purchase_date'),
            last_inspection=None,
            next_inspection=device_data.get('next_inspection'),
            status='active',
            notes=device_data.get('notes', ''),
            created_at=device_data.get('created_at')
        )
        
        # Speichere
        self.device_repository.save(device)
        return device


class GetDevicesDueForInspectionUseCase:
    """Use Case: Geräte mit fälliger Inspektion abrufen"""
    
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository
    
    def execute(self) -> List[Device]:
        return self.device_repository.find_due_for_inspection()
