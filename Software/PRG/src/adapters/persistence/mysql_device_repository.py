"""MySQL Device Repository Implementation - Mit Logging"""
import mysql.connector
import time
from typing import List, Optional
from datetime import datetime
import os
from src.core.domain.device import Device
from src.adapters.services.logger_service import LoggerService
from src.adapters.services.qr_code_generator import QRCodeGenerator


class MySQLDeviceRepository:
    """MySQL implementation of Device Repository - Mit Logging"""

    def __init__(self):
        self.logger = LoggerService()
        self.config = {
            'host': os.getenv('DB_HOST', 'benning-mysql'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'benning'),
            'password': os.getenv('DB_PASSWORD', 'benning'),
            'database': os.getenv('DB_NAME', 'benning_device_manager')
        }
        self.logger.info("MySQLDeviceRepository initialized", host=self.config['host'])

    def _get_connection(self):
        """Get database connection"""
        try:
            conn = mysql.connector.connect(**self.config)
            self.logger.debug("Database connection established")
            return conn
        except mysql.connector.Error as e:
            self.logger.error("Failed to connect to database", exception=e)
            raise

    def _row_to_device(self, row: dict) -> Device:
        """Convert database row to Device object"""
        if not row:
            return None
        return Device(
            id=row.get('id'),
            customer=row.get('customer'),
            device_id=row.get('device_id'),
            name=row.get('name'),
            type=row.get('type'),
            location=row.get('location'),
            manufacturer=row.get('manufacturer'),
            serial_number=row.get('serial_number'),
            purchase_date=row.get('purchase_date'),
            last_inspection=row.get('last_inspection'),
            next_inspection=row.get('next_inspection'),
            status=row.get('status', 'active'),
            qr_code=row.get('qr_code'),
            notes=row.get('notes'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )

    def _generate_device_id(self, customer: str) -> str:
        """Generate device ID with format: Customer-00001"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT COUNT(*) as count FROM devices WHERE customer = %s"
            cursor.execute(query, (customer,))
            result = cursor.fetchone()
            
            next_num = (result['count'] + 1) if result else 1
            device_id = f"{customer}-{next_num:05d}"
            
            cursor.close()
            conn.close()
            
            self.logger.debug(f"Generated device_id: {device_id}", customer=customer)
            return device_id
        except Exception as e:
            self.logger.error("Failed to generate device_id", exception=e)
            raise

    def get_all(self) -> List[Device]:
        """Get all devices"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM devices ORDER BY created_at DESC"
            cursor.execute(query)

            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation('SELECT', 'devices', 'success', duration_ms, count=len(results))
            
            return [self._row_to_device(row) for row in results]
        except Exception as e:
            self.logger.error("Failed to get all devices", exception=e)
            self.logger.log_db_operation('SELECT', 'devices', 'error', 0, error=str(e))
            return []

    def get_by_id(self, device_id: int) -> Optional[Device]:
        """Get device by ID"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM devices WHERE id = %s"
            cursor.execute(query, (device_id,))

            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation('SELECT', 'devices', 'success', duration_ms, device_id=device_id)
            
            return self._row_to_device(result)
        except Exception as e:
            self.logger.error(f"Failed to get device by id {device_id}", exception=e)
            return None

    def create(self, device: Device) -> Device:
        """Create new device and return it"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Generate device_id if not provided
            if not device.device_id and device.customer:
                device.device_id = self._generate_device_id(device.customer)
            
            # Generate QR-Code
            if device.device_id:
                qr_code_bytes = QRCodeGenerator.generate_qr_code(
                    device_id=device.device_id,
                    customer=device.customer or ""
                )
                if qr_code_bytes:
                    device.qr_code = qr_code_bytes
                    self.logger.debug(f"QR-Code generated for {device.device_id}")
            
            query = """
                INSERT INTO devices 
                (customer, device_id, name, type, location, manufacturer, serial_number, 
                 purchase_date, status, qr_code, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                device.customer if device.customer else None,
                device.device_id if device.device_id else None,
                device.name if device.name else None,
                device.type if device.type else None,
                device.location if device.location else None,
                device.manufacturer if device.manufacturer else None,
                device.serial_number if device.serial_number else None,
                device.purchase_date if device.purchase_date else None,
                device.status if device.status else 'active',
                device.qr_code if device.qr_code else None,
                device.notes if device.notes else None
            ))
            
            conn.commit()
            device.id = cursor.lastrowid
            cursor.close()
            conn.close()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation(
                'INSERT', 'devices', 'success', duration_ms,
                device_id=device.device_id,
                customer=device.customer
            )
            
            return device
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error("Failed to create device", exception=e)
            self.logger.log_db_operation('INSERT', 'devices', 'error', duration_ms, error=str(e))
            raise

    def update(self, device: Device) -> Device:
        """Update existing device"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                UPDATE devices 
                SET customer = %s, name = %s, type = %s, location = %s,
                    manufacturer = %s, serial_number = %s, purchase_date = %s,
                    status = %s, notes = %s, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(query, (
                device.customer,
                device.name,
                device.type,
                device.location,
                device.manufacturer,
                device.serial_number,
                device.purchase_date,
                device.status,
                device.notes,
                device.id
            ))

            conn.commit()
            cursor.close()
            conn.close()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation(
                'UPDATE', 'devices', 'success', duration_ms,
                device_id=device.device_id
            )
            
            return device
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error("Failed to update device", exception=e)
            self.logger.log_db_operation('UPDATE', 'devices', 'error', duration_ms, error=str(e))
            raise

    def delete(self, device_id: int) -> bool:
        """Delete device by ID"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM devices WHERE id = %s", (device_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation('DELETE', 'devices', 'success', duration_ms, device_id=device_id)
            
            return True
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error("Failed to delete device", exception=e)
            self.logger.log_db_operation('DELETE', 'devices', 'error', duration_ms, error=str(e))
            return False

    def get_next_id(self) -> str:
        """Get next device ID"""
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
            self.logger.error("Failed to get next_id", exception=e)
            return "1"



    def get_by_device_id(self, device_id: str) -> Optional[Device]:
        """Get device by device_id (e.g. Parloa-00001)"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM devices WHERE device_id = %s"
            cursor.execute(query, (device_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation('SELECT', 'devices', 'success', duration_ms, device_id=device_id)
            
            return self._row_to_device(result) if result else None
        except Exception as e:
            self.logger.error(f"Error getting device by device_id: {e}", exception=e)
            return None