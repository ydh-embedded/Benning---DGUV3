"""Device Entity - Hexagonal Architecture mit customer_device_id"""
from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Device:
    """Device Entity - Hexagonal Architecture
    
    Attributes:
        id: Numerische Datenbank-ID (auto-increment)
        customer: Kundenname (z.B. "Parloa")
        customer_device_id: Formatierte Kunden-ID (z.B. "Parloa-00001")
        name: Gerätename
        type: Gerätetyp (z.B. "Elektrowerkzeug")
        serial_number: Seriennummer (UNIQUE)
        manufacturer: Hersteller
        model: Modell
        location: Standort
        purchase_date: Kaufdatum
        last_inspection: Letzte Inspektion
        next_inspection: Nächste Inspektion
        status: Status (active, inactive, maintenance, retired)
        qr_code: QR-Code als Bytes (PNG/Base64)
        notes: Notizen
    """
    
    # ANCHOR: Required Fields
    id: Optional[int] = None
    name: str = ""
    customer: Optional[str] = None
    customer_device_id: Optional[str] = None
    
    # ANCHOR: Optional Fields
    type: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    purchase_date: Optional[date] = None
    last_inspection: Optional[date] = None
    next_inspection: Optional[date] = None
    status: str = "active"
    qr_code: Optional[bytes] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate device after initialization"""
        if not self.name:
            raise ValueError("Device name is required")
        if not self.customer:
            raise ValueError("Customer is required")
    
    def __str__(self) -> str:
        """String representation"""
        return f"Device({self.customer_device_id}: {self.name})"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return (
            f"Device(id={self.id}, customer_device_id={self.customer_device_id}, "
            f"name={self.name}, type={self.type}, status={self.status})"
        )
    
    def is_active(self) -> bool:
        """Check if device is active"""
        return self.status == "active"
    
    def is_due_for_inspection(self) -> bool:
        """Check if device is due for inspection"""
        if not self.next_inspection:
            return True
        from datetime import datetime
        return datetime.now().date() >= self.next_inspection
    
    def to_dict(self) -> dict:
        """Convert device to dictionary"""
        return {
            'id': self.id,
            'customer': self.customer,
            'customer_device_id': self.customer_device_id,
            'name': self.name,
            'type': self.type,
            'serial_number': self.serial_number,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'location': self.location,
            'purchase_date': str(self.purchase_date) if self.purchase_date else None,
            'last_inspection': str(self.last_inspection) if self.last_inspection else None,
            'next_inspection': str(self.next_inspection) if self.next_inspection else None,
            'status': self.status,
            'notes': self.notes
        }
