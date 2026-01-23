"""
Device Domain Model
Repräsentiert ein Gerät im System
"""
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Optional


@dataclass
class DeviceId:
    """Value Object für Device ID"""
    value: str
    
    def __post_init__(self):
        if not self.value.startswith('BENNING-'):
            raise ValueError("Device ID muss mit 'BENNING-' beginnen")
    
    def __str__(self):
        return self.value


@dataclass
class Device:
    """Device Entity"""
    id: DeviceId
    name: str
    type: str
    location: str
    manufacturer: str
    serial_number: str
    purchase_date: date
    last_inspection: Optional[date]
    next_inspection: date
    status: str  # 'active', 'inactive', 'retired'
    notes: str
    created_at: datetime
    
    def is_due_for_inspection(self) -> bool:
        """Prüfe, ob Inspektion fällig ist"""
        return datetime.now().date() >= self.next_inspection
    
    def schedule_next_inspection(self, interval_days: int = 365) -> date:
        """Plane nächste Inspektion"""
        return datetime.now().date() + timedelta(days=interval_days)
    
    def mark_as_inspected(self, inspection_date: date) -> None:
        """Markiere Gerät als inspiziert"""
        self.last_inspection = inspection_date
        self.next_inspection = self.schedule_next_inspection()
    
    def is_active(self) -> bool:
        """Prüfe, ob Gerät aktiv ist"""
        return self.status == 'active'
