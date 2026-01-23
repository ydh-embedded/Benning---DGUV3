"""
MySQL Device Repository Adapter
Konkrete Implementierung des Device Repository Ports
"""
from typing import List, Optional
import mysql.connector
from ...core.domain.device import Device, DeviceId
from ...core.ports.device_repository import DeviceRepository
from datetime import datetime, date


class MySQLDeviceRepository(DeviceRepository):
    """MySQL-basierte Implementierung des Device Repository"""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.connection = None
    
    def _get_connection(self):
        """Stelle Datenbankverbindung her"""
        if not self.connection or not self.connection.is_connected():
            self.connection = mysql.connector.connect(**self.db_config)
        return self.connection
    
    def find_by_id(self, device_id: DeviceId) -> Optional[Device]:
        """Finde Gerät nach ID"""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM devices WHERE id = %s", (str(device_id),))
            row = cursor.fetchone()
            
            if row:
                return self._map_to_device(row)
            return None
        finally:
            cursor.close()
    
    def find_all(self) -> List[Device]:
        """Finde alle Geräte"""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM devices ORDER BY id")
            rows = cursor.fetchall()
            return [self._map_to_device(row) for row in rows]
        finally:
            cursor.close()
    
    def find_active(self) -> List[Device]:
        """Finde alle aktiven Geräte"""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM devices WHERE status = 'active' ORDER BY id")
            rows = cursor.fetchall()
            return [self._map_to_device(row) for row in rows]
        finally:
            cursor.close()
    
    def find_due_for_inspection(self) -> List[Device]:
        """Finde Geräte, deren Inspektion fällig ist"""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT * FROM devices 
                WHERE status = 'active' AND next_inspection < CURDATE()
                ORDER BY next_inspection ASC
            """)
            rows = cursor.fetchall()
            return [self._map_to_device(row) for row in rows]
        finally:
            cursor.close()
    
    def save(self, device: Device) -> None:
        """Speichere Gerät"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO devices 
                (id, name, type, location, manufacturer, serial_number, 
                 purchase_date, last_inspection, next_inspection, status, notes, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name), type = VALUES(type), location = VALUES(location),
                manufacturer = VALUES(manufacturer), serial_number = VALUES(serial_number),
                purchase_date = VALUES(purchase_date), last_inspection = VALUES(last_inspection),
                next_inspection = VALUES(next_inspection), status = VALUES(status), notes = VALUES(notes)
            """, (
                str(device.id), device.name, device.type, device.location,
                device.manufacturer, device.serial_number, device.purchase_date,
                device.last_inspection, device.next_inspection, device.status,
                device.notes, device.created_at
            ))
            conn.commit()
        finally:
            cursor.close()
    
    def delete(self, device_id: DeviceId) -> None:
        """Lösche Gerät"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM devices WHERE id = %s", (str(device_id),))
            conn.commit()
        finally:
            cursor.close()
    
    def get_next_id(self) -> DeviceId:
        """Gebe nächste verfügbare Device ID zurück"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id FROM devices 
                WHERE id LIKE 'BENNING-%' 
                ORDER BY id DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            
            if result:
                last_id = result[0]
                number = int(last_id.split('-')[1]) + 1
                return DeviceId(f"BENNING-{number:03d}")
            else:
                return DeviceId("BENNING-001")
        finally:
            cursor.close()
    
    def _map_to_device(self, row: dict) -> Device:
        """Konvertiere Datenbankzeile zu Device-Objekt"""
        return Device(
            id=DeviceId(row['id']),
            name=row['name'],
            type=row['type'],
            location=row['location'],
            manufacturer=row.get('manufacturer', ''),
            serial_number=row.get('serial_number', ''),
            purchase_date=row.get('purchase_date'),
            last_inspection=row.get('last_inspection'),
            next_inspection=row.get('next_inspection'),
            status=row.get('status', 'active'),
            notes=row.get('notes', ''),
            created_at=row.get('created_at', datetime.now())
        )
    
    def close(self):
        """Schließe Datenbankverbindung"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
