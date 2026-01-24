"""Device Domain Model"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Device:
    """Device Entity"""
    id: str
    name: str
    type: Optional[str] = None
    location: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    last_inspection: Optional[date] = None
    next_inspection: Optional[date] = None
    status: str = 'active'
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'location': self.location,
            'manufacturer': self.manufacturer,
            'serial_number': self.serial_number,
            'purchase_date': self.purchase_date,
            'last_inspection': self.last_inspection,
            'next_inspection': self.next_inspection,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @staticmethod
    def from_dict(data: dict):
        """Create from dictionary"""
        return Device(
            id=data.get('id'),
            name=data.get('name'),
            type=data.get('type'),
            location=data.get('location'),
            manufacturer=data.get('manufacturer'),
            serial_number=data.get('serial_number'),
            purchase_date=data.get('purchase_date'),
            last_inspection=data.get('last_inspection'),
            next_inspection=data.get('next_inspection'),
            status=data.get('status', 'active'),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )
