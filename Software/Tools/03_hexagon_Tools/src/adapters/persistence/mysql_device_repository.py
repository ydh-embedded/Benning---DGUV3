"""MySQL Device Repository Adapter"""
from typing import List, Optional
import mysql.connector
from src.core.domain.device import Device
from src.core.ports.device_repository import DeviceRepository

class MySQLDeviceRepository(DeviceRepository):
    """MySQL Implementation of Device Repository"""

    def __init__(self, connection_config: dict):
        self.config = connection_config

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def get_by_id(self, device_id: int) -> Optional[Device]:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices WHERE id = %s", (device_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return self._map_to_device(result) if result else None

    def get_all(self) -> List[Device]:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [self._map_to_device(row) for row in results]

    def create(self, device: Device) -> Device:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO devices (name, device_type, serial_number, manufacturer, model, description) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (device.name, device.device_type, device.serial_number, device.manufacturer, device.model, device.description))
        device.id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return device

    def update(self, device: Device) -> Device:
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "UPDATE devices SET name=%s, device_type=%s, serial_number=%s, manufacturer=%s, model=%s, description=%s WHERE id=%s"
        cursor.execute(query, (device.name, device.device_type, device.serial_number, device.manufacturer, device.model, device.description, device.id))
        conn.commit()
        cursor.close()
        conn.close()
        return device

    def delete(self, device_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM devices WHERE id = %s", (device_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def get_by_serial(self, serial_number: str) -> Optional[Device]:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM devices WHERE serial_number = %s", (serial_number,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return self._map_to_device(result) if result else None

    def _map_to_device(self, row: dict) -> Device:
        return Device(
            id=row.get('id'),
            name=row.get('name', ''),
            device_type=row.get('device_type', ''),
            serial_number=row.get('serial_number', ''),
            manufacturer=row.get('manufacturer', ''),
            model=row.get('model', ''),
            description=row.get('description', ''),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
