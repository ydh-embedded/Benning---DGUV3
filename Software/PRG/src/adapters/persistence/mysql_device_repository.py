
import time
from typing import List, Optional
from src.core.domain.device import Device
from src.adapters.services.logger_service import LoggerService
import mysql.connector
from mysql.connector import Error


class MySQLDeviceRepository:
    """MySQL implementation of Device Repository"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.logger = LoggerService()
        self.logger.info("MySQLDeviceRepository initialized", host=host)
    
    def _get_connection(self):
        """Get MySQL connection"""
        try:
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return conn
        except Error as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    def create(self, device: Device) -> Device:
        """Create a new device"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Generate customer_device_id if not provided
            if not device.customer_device_id and device.customer:
                device.customer_device_id = self._generate_customer_device_id(device.customer)
            
            # FIX: Konvertiere leere Strings zu NULL für serial_number
            # Dies verhindert Duplicate-Fehler bei leeren Seriennummern
            if device.serial_number == "" or device.serial_number is None:
                device.serial_number = None
            
            # FIX: Konvertiere leere Strings zu NULL für purchase_date
            if device.purchase_date == "":
                device.purchase_date = None
            
            query = """
                INSERT INTO devices 
                (customer, customer_device_id, name, type, location, manufacturer, serial_number, purchase_date, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                device.customer,
                device.customer_device_id,
                device.name,
                device.type,
                device.location,
                device.manufacturer,
                device.serial_number,  # Jetzt NULL statt leerer String
                device.purchase_date,  # Jetzt NULL statt leerer String
                device.status or 'active',
                device.notes
            )
            
            cursor.execute(query, values)
            conn.commit()
            
            # Get the inserted ID
            device.id = cursor.lastrowid
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation(
                operation="INSERT",
                table="devices",
                result="success",
                duration_ms=duration_ms,
                customer_device_id=device.customer_device_id,
                customer=device.customer
            )
            
            cursor.close()
            conn.close()
            
            return device
        except Exception as e:
            self.logger.error(f"Failed to create device: {e}", exception=e)
            raise
    
    def get_by_id(self, device_id: int) -> Optional[Device]:
        """Get device by ID"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM devices WHERE id = %s"
            cursor.execute(query, (device_id,))
            result = cursor.fetchone()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation(
                operation="SELECT",
                table="devices",
                result="success" if result else "not_found",
                duration_ms=duration_ms
            )
            
            cursor.close()
            conn.close()
            
            if result:
                return self._map_to_device(result)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get device by id: {e}", exception=e)
            raise
    
    def get_by_customer_device_id(self, customer_device_id: str) -> Optional[Device]:
        """Get device by customer_device_id"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM devices WHERE customer_device_id = %s"
            cursor.execute(query, (customer_device_id,))
            result = cursor.fetchone()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation(
                operation="SELECT",
                table="devices",
                result="success" if result else "not_found",
                duration_ms=duration_ms,
                customer_device_id=customer_device_id
            )
            
            cursor.close()
            conn.close()
            
            if result:
                return self._map_to_device(result)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get device by customer_device_id: {e}", exception=e)
            raise
    
    def get_all(self) -> List[Device]:
        """Get all devices"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM devices ORDER BY id DESC"
            cursor.execute(query)
            results = cursor.fetchall()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation(
                operation="SELECT",
                table="devices",
                result="success",
                duration_ms=duration_ms,
                count=len(results)
            )
            
            cursor.close()
            conn.close()
            
            return [self._map_to_device(row) for row in results]
        except Exception as e:
            self.logger.error(f"Failed to get all devices: {e}", exception=e)
            raise
    
    def update(self, device: Device) -> Device:
        """Update an existing device"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # FIX: Konvertiere leere Strings zu NULL
            if device.serial_number == "":
                device.serial_number = None
            if device.purchase_date == "":
                device.purchase_date = None
            
            query = """
                UPDATE devices 
                SET customer = %s, customer_device_id = %s, name = %s, type = %s, 
                    location = %s, manufacturer = %s, serial_number = %s, 
                    purchase_date = %s, status = %s, notes = %s
                WHERE id = %s
            """
            
            values = (
                device.customer,
                device.customer_device_id,
                device.name,
                device.type,
                device.location,
                device.manufacturer,
                device.serial_number,
                device.purchase_date,
                device.status or 'active',
                device.notes,
                device.id
            )
            
            cursor.execute(query, values)
            conn.commit()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation(
                operation="UPDATE",
                table="devices",
                result="success",
                duration_ms=duration_ms,
                customer_device_id=device.customer_device_id
            )
            
            cursor.close()
            conn.close()
            
            return device
        except Exception as e:
            self.logger.error(f"Failed to update device: {e}", exception=e)
            raise
    
    def delete(self, customer_device_id: str) -> bool:
        """Delete a device"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "DELETE FROM devices WHERE customer_device_id = %s"
            cursor.execute(query, (customer_device_id,))
            conn.commit()
            
            rows_affected = cursor.rowcount
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation(
                operation="DELETE",
                table="devices",
                result="success",
                duration_ms=duration_ms,
                customer_device_id=customer_device_id
            )
            
            cursor.close()
            conn.close()
            
            return rows_affected > 0
        except Exception as e:
            self.logger.error(f"Failed to delete device: {e}", exception=e)
            raise
    
    def _generate_customer_device_id(self, customer: str) -> str:
        """Generate next customer_device_id"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT MAX(CAST(SUBSTRING(customer_device_id, LENGTH(%s) + 2) AS UNSIGNED)) as max_num
                FROM devices
                WHERE customer_device_id LIKE %s
            """
            
            pattern = f"{customer}-%"
            cursor.execute(query, (customer, pattern))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            max_num = result['max_num'] if result and result['max_num'] else 0
            next_num = max_num + 1
            
            return f"{customer}-{next_num:05d}"
        except Exception as e:
            self.logger.error(f"Failed to generate customer_device_id: {e}", exception=e)
            raise
    
    def _map_to_device(self, row: dict) -> Device:
        """Map database row to Device object"""
        return Device(
            id=row.get('id'),
            customer=row.get('customer'),
            customer_device_id=row.get('customer_device_id'),
            name=row.get('name'),
            type=row.get('type'),
            location=row.get('location'),
            manufacturer=row.get('manufacturer'),
            serial_number=row.get('serial_number'),
            purchase_date=row.get('purchase_date'),
            status=row.get('status'),
            notes=row.get('notes'),
            last_inspection=row.get('last_inspection'),
            next_inspection=row.get('next_inspection'),
            qr_code=row.get('qr_code')
        )
