#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benning Device Manager - Flask Application
Leichtgewichtige Web-Anwendung für Geräte-Management und DGUV3-Prüfungen
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Datenbank-Konfiguration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3307)),
    'user': os.getenv('DB_USER', 'benning'),
    'password': os.getenv('DB_PASSWORD', 'xxx xxx'),
    'database': os.getenv('DB_NAME', 'benning_device_manager'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_db_connection():
    """Erstellt Datenbankverbindung"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Datenbankfehler: {e}")
        return None

def get_next_device_id():
    """Generiert nächste Geräte-ID im Format BENNING-XXX"""
    conn = get_db_connection()
    if not conn:
        return "BENNING-001"
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM devices WHERE id LIKE 'BENNING-%' ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            last_id = result[0]
            number = int(last_id.split('-')[1]) + 1
            return f"BENNING-{number:03d}"
        else:
            return "BENNING-001"
    except Error as e:
        print(f"Fehler bei ID-Generierung: {e}")
        return "BENNING-001"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/')
def index():
    """Dashboard mit Statistiken"""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Datenbankverbindung fehlgeschlagen")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Statistiken abrufen
        cursor.execute("SELECT COUNT(*) as total FROM devices WHERE status = 'active'")
        total_devices = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM devices WHERE next_inspection < CURDATE() AND status = 'active'")
        overdue = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM inspections WHERE inspection_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
        recent_inspections = cursor.fetchone()['total']
        
        # Letzte Geräte
        cursor.execute("""
            SELECT id, name, type, location, status, next_inspection 
            FROM devices 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_devices = cursor.fetchall()
        
        return render_template('index.html',
                             total_devices=total_devices,
                             overdue=overdue,
                             recent_inspections=recent_inspections,
                             recent_devices=recent_devices)
    except Error as e:
        return render_template('error.html', message=f"Datenbankfehler: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/devices')
def devices():
    """Geräteliste"""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Datenbankverbindung fehlgeschlagen")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, type, location, manufacturer, serial_number, 
                   last_inspection, next_inspection, status 
            FROM devices 
            ORDER BY id
        """)
        devices = cursor.fetchall()
        
        return render_template('devices.html', devices=devices)
    except Error as e:
        return render_template('error.html', message=f"Datenbankfehler: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/quick-add')
def quick_add():
    """Schnellerfassung"""
    next_id = get_next_device_id()
    return render_template('quick_add.html', next_id=next_id)

@app.route('/api/devices', methods=['POST'])
def add_device():
    """Gerät hinzufügen"""
    data = request.json
    conn = get_db_connection()
    
    if not conn:
        return jsonify({'success': False, 'error': 'Datenbankverbindung fehlgeschlagen'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Berechne next_inspection (12 Monate ab heute)
        next_inspection = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO devices 
            (id, name, type, location, manufacturer, serial_number, 
             purchase_date, last_inspection, next_inspection, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('id'),
            data.get('name'),
            data.get('type'),
            data.get('location'),
            data.get('manufacturer'),
            data.get('serial_number'),
            data.get('purchase_date'),
            datetime.now().strftime('%Y-%m-%d'),
            next_inspection,
            'active',
            data.get('notes', '')
        ))
        
        conn.commit()
        
        # Nächste ID generieren
        next_id = get_next_device_id()
        
        return jsonify({'success': True, 'next_id': next_id})
    except Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/device/<device_id>')
def device_detail(device_id):
    """Gerätedetails"""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Datenbankverbindung fehlgeschlagen")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Gerät abrufen
        cursor.execute("SELECT * FROM devices WHERE id = %s", (device_id,))
        device = cursor.fetchone()
        
        if not device:
            return render_template('error.html', message="Gerät nicht gefunden"), 404
        
        # Prüfungen abrufen
        cursor.execute("""
            SELECT * FROM inspections 
            WHERE device_id = %s 
            ORDER BY inspection_date DESC
        """, (device_id,))
        inspections = cursor.fetchall()
        
        return render_template('device_detail.html', device=device, inspections=inspections)
    except Error as e:
        return render_template('error.html', message=f"Datenbankfehler: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/qr/<device_id>')
def generate_qr(device_id):
    """QR-Code generieren"""
    # URL zum Gerät
    device_url = request.host_url + f'device/{device_id}'
    
    # QR-Code erstellen
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(device_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # In BytesIO speichern
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@app.route('/health')
def health():
    """Health-Check Endpoint"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    else:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 503

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Benning Device Manager läuft auf http://0.0.0.0:5000")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
