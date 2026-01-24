"""
MySQL Device Repository mit Kunde und QR-Code Support
"""

import os
import mysql.connector
from mysql.connector import Error
from typing import Optional, List
from datetime import datetime


class MySQLDeviceRepository:
    """MySQL Repository für Device Persistierung"""
    
    def __init__(self):
        """Initialisiere mit Umgebungsvariablen"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3307))
        self.user = os.getenv('DB_USER', 'benning')
        self.password = os.getenv('DB_PASSWORD', 'benning')
        self.database = os.getenv('DB_NAME', 'benning_device_manager')
    
    def _get_connection(self):
        """Erstelle Datenbankverbindung"""
        try:
            return mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except Error as e:
            print(f"❌ Datenbankfehler: {e}")
            raise
    
    def get_next_sequence_for_customer(self, customer: str) -> int:
        """
        Ermittle nächste Sequenznummer für Kunde
        
        Args:
            customer: Kundenname
        
        Returns:
            Nächste Sequenznummer
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Zähle Geräte für diesen Kunden
            query = "SELECT COUNT(*) FROM devices WHERE customer = %s"
            cursor.execute(query, (customer,))
            count = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            return count + 1
        except Error as e:
            print(f"❌ Fehler beim Abrufen der Sequenznummer: {e}")
            return 1
    
    def generate_device_id(self, customer: str) -> str:
        """
        Generiere Device ID im Format "Kunde-00001"
        
        Args:
            customer: Kundenname
        
        Returns:
            Formatierte Device ID
        """
        sequence = self.get_next_sequence_for_customer(customer)
        formatted_number = str(sequence).zfill(5)
        return f"{customer}-{formatted_number}"
    
    def create(self, device) -> dict:
        """
        Erstelle neues Gerät
        
        Args:
            device: Device Objekt
        
        Returns:
            Dictionary mit Device und next_id
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            # Generiere Device ID
            device_id = self.generate_device_id(device.customer)
            device.device_id = device_id
            
            # Konvertiere leere Strings zu NULL
            purchase_date = device.purchase_date if device.purchase_date else None
            last_inspection = device.last_inspection if device.last_inspection else None
            next_inspection = device.next_inspection if device.next_inspection else None
            
            # Insert Device
            query = """
            INSERT INTO devices 
            (customer, device_id, name, type, serial_number, manufacturer, model, 
             location, purchase_date, last_inspection, next_inspection, status, 
             qr_code, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                device.customer,
                device_id,
                device.name,
                device.type,
                device.serial_number,
                device.manufacturer,
                device.model,
                device.location,
                purchase_date,
                last_inspection,
                next_inspection,
                device.status,
                device.qr_code,
                device.notes
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            # Hole neue ID
            device.id = cursor.lastrowid
            
            # Nächste ID für nächstes Gerät
            next_sequence = self.get_next_sequence_for_customer(device.customer)
            next_device_id = f"{device.customer}-{str(next_sequence).zfill(5)}"
            
            cursor.close()
            connection.close()
            
            return {
                'success': True,
                'device': device.to_dict(),
                'next_id': next_device_id
            }
        
        except Error as e:
            print(f"❌ Fehler beim Erstellen: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_by_id(self, device_id: int):
        """Hole Gerät nach ID"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            query = "SELECT * FROM devices WHERE id = %s"
            cursor.execute(query, (device_id,))
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if result:
                return self._map_row_to_device(result)
            return None
        
        except Error as e:
            print(f"❌ Fehler: {e}")
            return None
    
    def get_by_device_id(self, device_id: str):
        """Hole Gerät nach Device ID (z.B. Parloa-00001)"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            query = "SELECT * FROM devices WHERE device_id = %s"
            cursor.execute(query, (device_id,))
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            if result:
                return self._map_row_to_device(result)
            return None
        
        except Error as e:
            print(f"❌ Fehler: {e}")
            return None
    
    def get_all(self) -> List:
        """Hole alle Geräte"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            query = "SELECT * FROM devices ORDER BY customer, id"
            cursor.execute(query)
            results = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return [self._map_row_to_device(row) for row in results]
        
        except Error as e:
            print(f"❌ Fehler: {e}")
            return []
    
    def get_by_customer(self, customer: str) -> List:
        """Hole alle Geräte eines Kunden"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            query = "SELECT * FROM devices WHERE customer = %s ORDER BY id"
            cursor.execute(query, (customer,))
            results = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return [self._map_row_to_device(row) for row in results]
        
        except Error as e:
            print(f"❌ Fehler: {e}")
            return []
    
    def update(self, device) -> dict:
        """Aktualisiere Gerät"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            query = """
            UPDATE devices 
            SET name = %s, type = %s, serial_number = %s, manufacturer = %s,
                model = %s, location = %s, purchase_date = %s, 
                last_inspection = %s, next_inspection = %s, status = %s, 
                qr_code = %s, notes = %s
            WHERE id = %s
            """
            
            values = (
                device.name,
                device.type,
                device.serial_number,
                device.manufacturer,
                device.model,
                device.location,
                device.purchase_date if device.purchase_date else None,
                device.last_inspection if device.last_inspection else None,
                device.next_inspection if device.next_inspection else None,
                device.status,
                device.qr_code,
                device.notes,
                device.id
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return {'success': True, 'device': device.to_dict()}
        
        except Error as e:
            print(f"❌ Fehler: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete(self, device_id: int) -> bool:
        """Lösche Gerät"""
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            query = "DELETE FROM devices WHERE id = %s"
            cursor.execute(query, (device_id,))
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return True
        
        except Error as e:
            print(f"❌ Fehler: {e}")
            return False
    
    def _map_row_to_device(self, row):
        """Konvertiere DB Row zu Device Objekt"""
        from device_WITH_CUSTOMER import Device
        
        return Device(
            id=row[0],
            customer=row[1],
            device_id=row[2],
            name=row[3],
            type=row[4],
            serial_number=row[5],
            manufacturer=row[6],
            model=row[7],
            location=row[8],
            purchase_date=row[9],
            last_inspection=row[10],
            next_inspection=row[11],
            status=row[12],
            qr_code=row[13],
            notes=row[14],
            created_at=row[15],
            updated_at=row[16]
        )
