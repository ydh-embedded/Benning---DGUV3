"""Device Use Cases"""
from typing import List, Optional
from src.core.domain.device import Device
from src.core.ports.device_repository import DeviceRepository

class GetDeviceUseCase:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository
    def execute(self, device_id: int) -> Optional[Device]:
        return self.repository.get_by_id(device_id)

class ListDevicesUseCase:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository
    def execute(self) -> List[Device]:
        return self.repository.get_all()

class CreateDeviceUseCase:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository
    def execute(self, device: Device) -> Device:
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
