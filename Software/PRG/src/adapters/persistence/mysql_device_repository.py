import mysql.connector
import time
from typing import List, Optional
from src.core.domain.device import Device
from src.adapters.services.logger_service import LoggerService
from mysql.connector import Error


class MySQLDeviceRepository:
    """MySQL implementation of Device Repository"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """Initialize MySQL Device Repository with database credentials"""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.logger = LoggerService()
        self.logger.info("MySQLDeviceRepository initialized", host=host)
    
    def _get_connection(self):
        """Get MySQL connection with error handling"""
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
        """Create a new device with proper error handling"""
        try:
            start_time = time.time()
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Generate customer_device_id if not provided
            if not device.customer_device_id and device.customer:
                device.customer_device_id = self.get_next_customer_device_id(device.customer)
            
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
                device.serial_number,
                device.purchase_date,
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
        except mysql.connector.errors.IntegrityError as e:
            self.logger.error(f"Duplicate entry error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create device: {e}", exception=e)
            raise
    
    def get_by_id(self, device_id: int) -> Optional[Device]:
        """Get device by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM devices WHERE id = %s"
            cursor.execute(query, (device_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return self._map_to_device(row)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get device by ID: {e}", exception=e)
            raise
    
    def get_by_customer_device_id(self, customer_device_id: str) -> Optional[Device]:
        """Get device by customer_device_id"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM devices WHERE customer_device_id = %s"
            cursor.execute(query, (customer_device_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return self._map_to_device(row)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get device by customer_device_id: {e}", exception=e)
            raise
    
    def list_all(self) -> List[Device]:
        """Get all devices"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM devices ORDER BY id DESC"
            cursor.execute(query)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            devices = [self._map_to_device(row) for row in rows]
            return devices
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
                SET customer = %s, name = %s, type = %s, location = %s, 
                    manufacturer = %s, serial_number = %s, purchase_date = %s, 
                    status = %s, notes = %s
                WHERE id = %s
            """
            
            values = (
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
            )
            
            cursor.execute(query, values)
            conn.commit()
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation(
                operation="UPDATE",
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
            self.logger.error(f"Failed to update device: {e}", exception=e)
            raise
    
    def delete(self, customer_device_id: str) -> bool:
        """Delete a device by customer_device_id"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM devices WHERE customer_device_id = %s"
            cursor.execute(query, (customer_device_id,))
            conn.commit()
            
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            
            return affected_rows > 0
        except Exception as e:
            self.logger.error(f"Failed to delete device: {e}", exception=e)
            raise
    
    def get_next_customer_device_id(self, customer: str) -> str:
        """Get next customer device ID with Database-Level Locking"""
        conn = None
        try:
            conn = self._get_connection()
            conn.start_transaction(isolation_level='READ COMMITTED')
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT MAX(CAST(SUBSTRING_INDEX(customer_device_id, '-', -1) AS UNSIGNED)) as max_num 
                FROM devices 
                WHERE customer = %s AND customer_device_id LIKE %s
                FOR UPDATE
            """
            
            cursor.execute(query, (customer, f"{customer}-%"))
            result = cursor.fetchone()
            
            max_num = result['max_num'] if result and result['max_num'] else 0
            next_num = max_num + 1
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return f"{customer}-{next_num:05d}"
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            self.logger.error(f"Failed to get next customer device ID: {e}", exception=e)
            import time
            return f"{customer}-{int(time.time() % 100000):05d}"
    
    def _map_to_device(self, row: dict) -> Device:
        """Map database row to Device domain object"""
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
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
