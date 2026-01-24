"""MySQL Device Repository Implementation"""
import mysql.connector
from typing import List, Optional
from datetime import datetime
import os
from src.core.domain.device import Device


class MySQLDeviceRepository:
    """MySQL implementation of Device Repository"""

    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3307)),
            'user': os.getenv('DB_USER', 'benning'),
            'password': os.getenv('DB_PASSWORD', 'benning'),
            'database': os.getenv('DB_NAME', 'benning_device_manager')
        }

    def _get_connection(self):
        """Get database connection"""
        return mysql.connector.connect(**self.config)

    def _row_to_device(self, row: dict) -> Device:
        """Convert database row to Device object"""
        if not row:
            return None
        return Device(
            id=row.get('id'),
            name=row.get('name'),
            type=row.get('type'),
            location=row.get('location'),
            manufacturer=row.get('manufacturer'),
            serial_number=row.get('serial_number'),
            purchase_date=row.get('purchase_date'),
            last_inspection=row.get('last_inspection'),
            next_inspection=row.get('next_inspection'),
            status=row.get('status', 'active'),
            notes=row.get('notes'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
        )

    def create(self, device: Device) -> Device:
        """Create new device and return it"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO devices 
                (id, name, type, location, manufacturer, serial_number, 
                 purchase_date, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(query, (
                device.id,
                device.name if device.name else None,
                device.type if device.type else None,
                device.location if device.location else None,
                device.manufacturer if device.manufacturer else None,
                device.serial_number if device.serial_number else None,
                device.purchase_date if device.purchase_date else None,
                device.status if device.status else 'active',
                device.notes if device.notes else None
            ))

            conn.commit()
            cursor.close()
            conn.close()
            
            # Gebe das Device Objekt zurück
            return device
        except Exception as e:
            print(f"Error creating device: {e}")
            raise

    def get_by_id(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM devices WHERE id = %s"
            cursor.execute(query, (device_id,))

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            return self._row_to_device(result)
        except Exception as e:
            print(f"Error getting device: {e}")
            return None

    def get_all(self) -> List[Device]:
        """Get all devices"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM devices ORDER BY created_at DESC"
            cursor.execute(query)

            results = cursor.fetchall()
            cursor.close()
            conn.close()

            return [self._row_to_device(row) for row in results]
        except Exception as e:
            print(f"Error getting all devices: {e}")
            return []

    def update(self, device: Device) -> Device:
        """Update device and return it"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                UPDATE devices 
                SET name = %s, type = %s, location = %s, manufacturer = %s,
                    serial_number = %s, purchase_date = %s, status = %s, notes = %s,
                    updated_at = NOW()
                WHERE id = %s
            """

            cursor.execute(query, (
                device.name if device.name else None,
                device.type if device.type else None,
                device.location if device.location else None,
                device.manufacturer if device.manufacturer else None,
                device.serial_number if device.serial_number else None,
                device.purchase_date if device.purchase_date else None,
                device.status if device.status else 'active',
                device.notes if device.notes else None,
                device.id
            ))

            conn.commit()
            cursor.close()
            conn.close()
            
            # Gebe das aktualisierte Device zurück
            return self.get_by_id(device.id)
        except Exception as e:
            print(f"Error updating device: {e}")
            raise

    def delete(self, device_id: str) -> bool:
        """Delete device"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = "DELETE FROM devices WHERE id = %s"
            cursor.execute(query, (device_id,))

            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting device: {e}")
            return False

    def get_recent(self, limit: int = 10) -> List[Device]:
        """Get recent devices"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM devices ORDER BY created_at DESC LIMIT %s"
            cursor.execute(query, (limit,))

            results = cursor.fetchall()
            cursor.close()
            conn.close()

            return [self._row_to_device(row) for row in results]
        except Exception as e:
            print(f"Error getting recent devices: {e}")
            return []

    def get_by_status(self, status: str) -> List[Device]:
        """Get devices by status"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM devices WHERE status = %s ORDER BY created_at DESC"
            cursor.execute(query, (status,))

            results = cursor.fetchall()
            cursor.close()
            conn.close()

            return [self._row_to_device(row) for row in results]
        except Exception as e:
            print(f"Error getting devices by status: {e}")
            return []

    def get_next_id(self) -> str:
        """Get next device ID (increment by 1)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT MAX(CAST(id AS UNSIGNED)) as max_id FROM devices WHERE id REGEXP '^[0-9]+$'"
            cursor.execute(query)

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            max_id = result.get('max_id') if result else 0
            next_id = (max_id or 0) + 1
            return str(next_id)
        except Exception as e:
            print(f"Error getting next ID: {e}")
            return "1"
