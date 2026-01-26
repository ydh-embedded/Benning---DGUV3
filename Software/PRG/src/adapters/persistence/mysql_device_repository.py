"""MySQL Device Repository - MIT DATABASE-LEVEL LOCKING FÜR RACE CONDITIONS"""
import time
from typing import Optional, List
from src.core.domain.device import Device
from src.adapters.services.logger_service import LoggerService
import mysql.connector


class MySQLDeviceRepository:
    """MySQL implementation of Device Repository with proper locking"""
    
    def __init__(self, db_host: str, db_port: int, db_user: str, db_password: str, db_name: str):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.logger = LoggerService()
    
    def _get_connection(self):
        """Get database connection"""
        return mysql.connector.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name
        )
    
    def create(self, device: Device) -> Device:
        """Create a new device"""
        start_time = time.time()
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Generate customer_device_id if not provided
            if not device.customer_device_id and device.customer:
                device.customer_device_id = self.get_next_customer_device_id(device.customer)
            
            # Konvertiere leere Strings zu NULL
            if device.serial_number == "" or device.serial_number is None:
                device.serial_number = None
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
                duration_ms=duration_ms,
                device_id=device_id
            )
            
            cursor.close()
            conn.close()
            
            if result:
                return Device(
                    id=result['id'],
                    customer=result['customer'],
                    customer_device_id=result['customer_device_id'],
                    name=result['name'],
                    type=result['type'],
                    location=result['location'],
                    manufacturer=result['manufacturer'],
                    serial_number=result['serial_number'],
                    purchase_date=result['purchase_date'],
                    last_inspection=result.get('last_inspection'),
                    next_inspection=result.get('next_inspection'),
                    status=result['status'],
                    notes=result['notes']
                )
            return None
        except Exception as e:
            self.logger.error(f"Failed to get device by ID: {e}", exception=e)
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
                return Device(
                    id=result['id'],
                    customer=result['customer'],
                    customer_device_id=result['customer_device_id'],
                    name=result['name'],
                    type=result['type'],
                    location=result['location'],
                    manufacturer=result['manufacturer'],
                    serial_number=result['serial_number'],
                    purchase_date=result['purchase_date'],
                    last_inspection=result.get('last_inspection'),
                    next_inspection=result.get('next_inspection'),
                    status=result['status'],
                    notes=result['notes']
                )
            return None
        except Exception as e:
            self.logger.error(f"Failed to get device by customer_device_id: {e}", exception=e)
            raise
    
    def list_all(self) -> List[Device]:
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
            
            devices = []
            for result in results:
                device = Device(
                    id=result['id'],
                    customer=result['customer'],
                    customer_device_id=result['customer_device_id'],
                    name=result['name'],
                    type=result['type'],
                    location=result['location'],
                    manufacturer=result['manufacturer'],
                    serial_number=result['serial_number'],
                    purchase_date=result['purchase_date'],
                    last_inspection=result.get('last_inspection'),
                    next_inspection=result.get('next_inspection'),
                    status=result['status'],
                    notes=result['notes']
                )
                devices.append(device)
            
            return devices
        except Exception as e:
            self.logger.error(f"Failed to list devices: {e}", exception=e)
            raise
    
    def update(self, device: Device) -> Device:
        """Update an existing device"""
        start_time = time.time()
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Konvertiere leere Strings zu NULL
            if device.serial_number == "":
                device.serial_number = None
            if device.purchase_date == "":
                device.purchase_date = None
            
            query = """
                UPDATE devices 
                SET customer = %s, name = %s, type = %s, location = %s, 
                    manufacturer = %s, serial_number = %s, purchase_date = %s, 
                    status = %s, notes = %s
                WHERE customer_device_id = %s
            """
            
            values = (
                device.customer,
                device.name,
                device.type,
                device.location,
                device.manufacturer,
                device.serial_number,
                device.purchase_date,
                device.status or 'active',
                device.notes,
                device.customer_device_id
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
        start_time = time.time()
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM devices WHERE customer_device_id = %s"
            cursor.execute(query, (customer_device_id,))
            conn.commit()
            
            success = cursor.rowcount > 0
            
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_db_operation(
                operation="DELETE",
                table="devices",
                result="success" if success else "not_found",
                duration_ms=duration_ms,
                customer_device_id=customer_device_id
            )
            
            cursor.close()
            conn.close()
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete device: {e}", exception=e)
            raise
    
    def get_next_customer_device_id(self, customer: str) -> str:
        """
        Get next customer device ID with DATABASE-LEVEL LOCKING to prevent race conditions.
        
        ✅ FIX: Verwendet FOR UPDATE um Race Conditions zu vermeiden
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                conn = self._get_connection()
                cursor = conn.cursor(dictionary=True)
                
                # ✅ FIX: Starte eine Transaktion mit Locking
                conn.start_transaction(isolation_level='READ COMMITTED')
                
                # Hole die höchste Nummer mit Locking (FOR UPDATE)
                query = """
                    SELECT MAX(CAST(SUBSTRING_INDEX(customer_device_id, '-', -1) AS UNSIGNED)) as max_num 
                    FROM devices 
                    WHERE customer = %s AND customer_device_id LIKE %s
                    FOR UPDATE
                """
                
                pattern = f"{customer}-%"
                cursor.execute(query, (customer, pattern))
                result = cursor.fetchone()
                
                max_num = result.get('max_num') if result else 0
                next_num = (max_num or 0) + 1
                
                # Format as "Customer-00001"
                next_id = f"{customer}-{next_num:05d}"
                
                # ✅ FIX: Commit die Transaktion
                conn.commit()
                
                self.logger.debug(f"Generated customer_device_id: {next_id}", customer=customer)
                
                cursor.close()
                conn.close()
                
                return next_id
            
            except mysql.connector.Error as e:
                retry_count += 1
                if retry_count < max_retries and e.errno == 1213:  # Deadlock
                    # Warte kurz und versuche es erneut
                    time.sleep(0.1 * retry_count)
                    continue
                
                self.logger.error(f"Failed to get next customer_device_id: {e}", exception=e)
                return f"{customer}-00001"
            
            except Exception as e:
                self.logger.error(f"Failed to get next customer_device_id: {e}", exception=e)
                return f"{customer}-00001"
        
        self.logger.error(f"Failed to get next customer_device_id after {max_retries} retries")
        return f"{customer}-00001"
