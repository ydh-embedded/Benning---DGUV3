"""
Benning Device Manager - Datenbank Initializer
Automatische Datenbank-Initialisierung und Cleanup
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from pathlib import Path
from datetime import datetime


class DatabaseInitializer:
    """Verwaltet Datenbank-Initialisierung und Cleanup"""
    
    def __init__(self):
        """Initialisiere mit Umgebungsvariablen"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3307))
        self.user = os.getenv('DB_USER', 'benning')
        self.password = os.getenv('DB_PASSWORD', 'benning')
        self.database = os.getenv('DB_NAME', 'benning_device_manager')
        self.root_password = os.getenv('DB_ROOT_PASSWORD', 'root')
        
    def connect_root(self):
        """Verbinde als root (für Datenbank-Erstellung)"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user='root',
                password=self.root_password
            )
            return connection
        except Error as e:
            print(f"❌ Fehler beim Root-Verbindung: {e}")
            return None
    
    def connect_user(self):
        """Verbinde als Benutzer"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            print(f"❌ Fehler beim Benutzer-Verbindung: {e}")
            return None
    
    def execute_sql_file(self, connection, sql_file):
        """Führe SQL-Datei aus"""
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            cursor = connection.cursor()
            
            # Teile SQL in einzelne Statements
            statements = sql_content.split(';')
            
            for statement in statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ SQL Fehler: {e}")
            return False
    
    def initialize_database(self):
        """Initialisiere Datenbank mit Schema"""
        print("\n📋 Initialisiere Datenbank...")
        
        # Verbinde als root
        connection = self.connect_root()
        if not connection:
            return False
        
        # Finde SQL-Datei
        sql_file = Path(__file__).parent / 'benning_schema_IDEMPOTENT.sql'
        
        if not sql_file.exists():
            print(f"❌ SQL-Datei nicht gefunden: {sql_file}")
            return False
        
        # Führe Schema aus
        if self.execute_sql_file(connection, sql_file):
            print("✅ Datenbank-Schema erstellt")
            connection.close()
            return True
        else:
            connection.close()
            return False
    
    def clear_devices(self):
        """Lösche alle Geräte (Cleanup)"""
        print("\n🗑️  Lösche alte Daten...")
        
        connection = self.connect_user()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # Lösche Daten (Foreign Keys beachten)
            cursor.execute("DELETE FROM audit_log;")
            cursor.execute("DELETE FROM inspections;")
            cursor.execute("DELETE FROM devices;")
            
            # Setze Auto-Increment zurück
            cursor.execute("ALTER TABLE devices AUTO_INCREMENT = 1;")
            cursor.execute("ALTER TABLE inspections AUTO_INCREMENT = 1;")
            cursor.execute("ALTER TABLE audit_log AUTO_INCREMENT = 1;")
            
            connection.commit()
            cursor.close()
            
            print("✅ Alte Daten gelöscht")
            return True
        except Error as e:
            print(f"❌ Fehler beim Löschen: {e}")
            return False
        finally:
            connection.close()
    
    def verify_connection(self):
        """Überprüfe Datenbankverbindung"""
        print("\n🔍 Überprüfe Datenbankverbindung...")
        
        connection = self.connect_user()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM devices;")
            count = cursor.fetchone()[0]
            cursor.close()
            
            print(f"✅ Verbindung OK - {count} Geräte in DB")
            return True
        except Error as e:
            print(f"❌ Fehler: {e}")
            return False
        finally:
            connection.close()
    
    def get_db_status(self):
        """Zeige Datenbank-Status"""
        print("\n📊 Datenbank-Status:")
        
        connection = self.connect_user()
        if not connection:
            return
        
        try:
            cursor = connection.cursor()
            
            # Zähle Einträge
            cursor.execute("SELECT COUNT(*) FROM devices;")
            devices = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM inspections;")
            inspections = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users;")
            users = cursor.fetchone()[0]
            
            cursor.close()
            
            print(f"  Geräte: {devices}")
            print(f"  Inspektionen: {inspections}")
            print(f"  Benutzer: {users}")
        except Error as e:
            print(f"❌ Fehler: {e}")
        finally:
            connection.close()
    
    def run_full_initialization(self, clean=False):
        """Führe vollständige Initialisierung durch"""
        print("\n" + "="*60)
        print("🚀 Benning Device Manager - Datenbank Initializer")
        print("="*60)
        
        # 1. Initialisiere Schema
        if not self.initialize_database():
            return False
        
        # 2. Optional: Cleanup
        if clean:
            if not self.clear_devices():
                return False
        
        # 3. Überprüfe Verbindung
        if not self.verify_connection():
            return False
        
        # 4. Zeige Status
        self.get_db_status()
        
        print("\n" + "="*60)
        print("✅ Initialisierung abgeschlossen!")
        print("="*60 + "\n")
        
        return True


def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Benning Device Manager - Datenbank Initializer'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Lösche alle Geräte vor Initialisierung'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Zeige nur Datenbank-Status'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Lösche alle Geräte'
    )
    
    args = parser.parse_args()
    
    initializer = DatabaseInitializer()
    
    if args.status:
        initializer.verify_connection()
        initializer.get_db_status()
    elif args.clear:
        initializer.clear_devices()
    else:
        initializer.run_full_initialization(clean=args.clean)


if __name__ == '__main__':
    main()
