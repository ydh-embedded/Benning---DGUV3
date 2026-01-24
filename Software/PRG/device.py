"""
Benning Device Manager - Device Domain Model
Mit Kunde und QR-Code Support
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Device:
    """Device Domain Model mit Kunde und QR-Code"""
    
    name: str
    customer: str  # NEU: Kundenname
    type: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    purchase_date: Optional[str] = None
    last_inspection: Optional[str] = None
    next_inspection: Optional[str] = None
    status: str = 'active'
    notes: Optional[str] = None
    id: Optional[int] = None
    device_id: Optional[str] = None  # NEU: Formatierte ID (Kunde-00001)
    qr_code: Optional[str] = None  # NEU: QR-Code als Base64
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validierung nach Initialisierung"""
        if not self.name:
            raise ValueError("Device name is required")
        if not self.customer:
            raise ValueError("Customer name is required")
        if self.status not in ['active', 'inactive', 'maintenance', 'retired']:
            raise ValueError(f"Invalid status: {self.status}")
    
    def generate_device_id(self, sequence_number: int) -> str:
        """
        Generiere formatierte Device ID
        
        Args:
            sequence_number: Sequenznummer (z.B. 1, 2, 3...)
        
        Returns:
            Formatierte ID (z.B. "Parloa-00001")
        """
        formatted_number = str(sequence_number).zfill(5)
        self.device_id = f"{self.customer}-{formatted_number}"
        return self.device_id
    
    def set_qr_code(self, qr_code_base64: str) -> None:
        """
        Setze QR-Code (als Base64 String)
        
        Args:
            qr_code_base64: QR-Code als Base64 String
        """
        self.qr_code = qr_code_base64
    
    def to_dict(self) -> dict:
        """Konvertiere zu Dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'customer': self.customer,
            'type': self.type,
            'serial_number': self.serial_number,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'location': self.location,
            'purchase_date': self.purchase_date,
            'last_inspection': self.last_inspection,
            'next_inspection': self.next_inspection,
            'status': self.status,
            'notes': self.notes,
            'qr_code': self.qr_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Device':
        """Erstelle Device aus Dictionary"""
        return cls(
            id=data.get('id'),
            device_id=data.get('device_id'),
            name=data.get('name'),
            customer=data.get('customer'),
            type=data.get('type'),
            serial_number=data.get('serial_number'),
            manufacturer=data.get('manufacturer'),
            model=data.get('model'),
            location=data.get('location'),
            purchase_date=data.get('purchase_date'),
            last_inspection=data.get('last_inspection'),
            next_inspection=data.get('next_inspection'),
            status=data.get('status', 'active'),
            notes=data.get('notes'),
            qr_code=data.get('qr_code'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )
    
    def __repr__(self) -> str:
        return (
            f"Device(id={self.id}, device_id={self.device_id}, "
            f"name={self.name}, customer={self.customer}, "
            f"type={self.type}, status={self.status})"
        )
