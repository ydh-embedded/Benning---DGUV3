"""Device Use Cases - Hexagonal Architecture"""
from src.core.domain.device import Device
from src.core.ports.device_repository import DeviceRepository
from src.adapters.services.qr_code_generator import QRCodeGenerator
from typing import List, Optional


class ListDevicesUseCase:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository
    
    def execute(self) -> List[Device]:
        return self.repository.get_all()


class GetDeviceUseCase:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository
    
    def execute(self, device_id: str) -> Optional[Device]:
        return self.repository.get_by_id(device_id)


class CreateDeviceUseCase:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository
    
    def execute(self, device: Device) -> Device:
        # Generiere QR-Code wenn device_id vorhanden ist
        if device.device_id:
            qr_code_bytes = QRCodeGenerator.generate_qr_code(
                device_id=device.device_id,
                customer=device.customer or ""
            )
            if qr_code_bytes:
                device.qr_code = qr_code_bytes
        
        return self.repository.create(device)


class UpdateDeviceUseCase:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository
    
    def execute(self, device: Device) -> Device:
        return self.repository.update(device)


class DeleteDeviceUseCase:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository
    
    def execute(self, device_id: int) -> bool:
        return self.repository.delete(device_id)