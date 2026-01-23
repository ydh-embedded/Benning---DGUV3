"""Device Domain Model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Device:
    """Device Entity"""
    id: Optional[int] = None
    name: str = ""
    device_type: str = ""
    serial_number: str = ""
    manufacturer: str = ""
    model: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def update(self, **kwargs):
        """Aktualisiere Device-Attribute"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def __repr__(self):
        return f"Device(id={self.id}, name={self.name}, serial={self.serial_number})"
