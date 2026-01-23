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
import json
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Lade Umgebungsvariablen
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads/usbc'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Datenbank-Konfiguration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3307)),
    'user': os.getenv('DB_USER', 'benning'),
    'password': os.getenv('DB_PASSWORD', 'benning'),
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

# ============================================================================
# USB-C KABEL-PRÜFUNG ERWEITERUNG
# ============================================================================

@app.route('/usbc-inspections')
def usbc_inspections_list():
    """Liste aller USB-C Prüfungen"""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Datenbankverbindung fehlgeschlagen")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            u.id,
            u.test_date,
            u.inspector_name,
            u.test_result,
            u.all_tests_passed,
            d.id as device_id,
            d.name as device_name,
            COUNT(DISTINCT r.id) as resistance_count,
            COUNT(DISTINCT p.id) as protocol_count
        FROM usbc_inspections u
        JOIN inspections i ON u.inspection_id = i.id
        JOIN devices d ON i.device_id = d.id
        LEFT JOIN usbc_resistance_tests r ON u.id = r.usbc_inspection_id
        LEFT JOIN usbc_protocol_tests p ON u.id = p.usbc_inspection_id
        GROUP BY u.id
        ORDER BY u.test_date DESC
    """)
    
    inspections = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('usbc_inspections_list.html', inspections=inspections)

@app.route('/device/<device_id>/usbc-inspection', methods=['GET'])
def usbc_inspection(device_id):
    """Zeige USB-C Prüfungsformular"""
    conn = get_db_connection()
    if not conn:
        return render_template('error.html', message="Datenbankverbindung fehlgeschlagen")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM devices WHERE id = %s", (device_id,))
    device = cursor.fetchone()
    
    if not device:
        cursor.close()
        conn.close()
        return "Gerät nicht gefunden", 404
    
    cursor.close()
    conn.close()
    return render_template('usbc_inspection.html', device=device)

@app.route('/device/<device_id>/usbc-inspection', methods=['POST'])
def save_usbc_inspection(device_id):
    """Speichere USB-C Prüfungsergebnisse"""
    conn = get_db_connection()
    if not conn:
        return "Datenbankverbindung fehlgeschlagen", 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Basis-Prüfung erstellen
        inspection_date = datetime.now().date()
        inspector_name = request.form.get('inspector_name')
        test_result = request.form.get('test_result', 'passed')
        notes = request.form.get('notes', '')
        
        cursor.execute("""
            INSERT INTO inspections (device_id, inspection_date, inspector_name, result, notes, next_inspection_date)
            VALUES (%s, %s, %s, %s, %s, DATE_ADD(%s, INTERVAL 1 YEAR))
        """, (device_id, inspection_date, inspector_name, test_result, notes, inspection_date))
        
        conn.commit()
        inspection_id = cursor.lastrowid
        
        # 2. USB-C spezifische Daten
        device_functional = 1 if request.form.get('device_functional') else 0
        battery_checked = 1 if request.form.get('battery_checked') else 0
        cable_visual_ok = 1 if request.form.get('cable_visual_ok') else 0
        cable_id = request.form.get('cable_id', device_id)
        
        cable_connected = 1 if request.form.get('cable_connected') else 0
        basic_functions_ok = 1 if request.form.get('basic_functions_ok') else 0
        
        # Protokolle als JSON
        protocols = request.form.getlist('protocols')
        protocols_json = json.dumps(protocols)
        
        resistance_test_done = 1 if request.form.get('resistance_test_done') else 0
        emarker_present = 1 if request.form.get('emarker_present') else 0
        
        # eMarker Daten als JSON
        emarker_data = None
        if emarker_present:
            emarker_data = json.dumps({
                'vendor': request.form.get('emarker_vendor', ''),
                'product': request.form.get('emarker_product', ''),
                'max_current': request.form.get('emarker_current', ''),
                'max_voltage': request.form.get('emarker_voltage', '')
            })
        
        # Foto-Upload
        pinout_photo_path = None
        if 'pinout_photo' in request.files:
            file = request.files['pinout_photo']
            if file and file.filename and allowed_file(file.filename):
                import os
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(f"{device_id}_{timestamp}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                file.save(filepath)
                pinout_photo_path = filepath
        
        all_tests_passed = (
            device_functional and battery_checked and cable_visual_ok and
            cable_connected and basic_functions_ok
        )
        
        cursor.execute("""
            INSERT INTO usbc_inspections (
                inspection_id, device_functional, battery_checked, cable_visual_ok, cable_id,
                cable_connected, basic_functions_ok, protocols_detected,
                pinout_photo_path, resistance_test_done, emarker_present, emarker_data,
                all_tests_passed, test_result, test_date, inspector_name, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            inspection_id, device_functional, battery_checked, cable_visual_ok, cable_id,
            cable_connected, basic_functions_ok, protocols_json,
            pinout_photo_path, resistance_test_done, emarker_present, emarker_data,
            all_tests_passed, test_result, inspection_date, inspector_name, notes
        ))
        
        conn.commit()
        usbc_inspection_id = cursor.lastrowid
        
        # 3. Widerstandsmessungen speichern
        if resistance_test_done:
            pin_measurements = [
                ('VBUS', request.form.get('pin_vbus'), 0.0, 0.5),
                ('GND', request.form.get('pin_gnd'), 0.0, 0.3),
                ('CC1', request.form.get('pin_cc1'), 0.8, 1.2),
                ('CC2', request.form.get('pin_cc2'), 0.8, 1.2),
                ('TX1+', request.form.get('pin_tx1p'), 0.0, 0.3),
                ('TX1-', request.form.get('pin_tx1n'), 0.0, 0.3),
                ('RX1+', request.form.get('pin_rx1p'), 0.0, 0.3),
                ('RX1-', request.form.get('pin_rx1n'), 0.0, 0.3),
            ]
            
            for pin_name, value_str, min_val, max_val in pin_measurements:
                if value_str:
                    try:
                        value = float(value_str)
                        passed = min_val <= value <= max_val
                        
                        cursor.execute("""
                            INSERT INTO usbc_resistance_tests 
                            (usbc_inspection_id, pin_name, resistance_value, expected_min, expected_max, passed)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (usbc_inspection_id, pin_name, value, min_val, max_val, passed))
                    except ValueError:
                        pass
        
        # 4. Protokoll-Tests speichern
        protocol_details = {
            'USB 2.0': (480, False, None),
            'USB 3.2 Gen 2': (10000, False, None),
            'DisplayPort Alt Mode': (None, False, None),
            'Power Delivery 3.0': (None, True, 100),
            'Thunderbolt 4': (40000, True, 100),
        }
        
        for protocol in protocols:
            if protocol in protocol_details:
                speed, pd, power = protocol_details[protocol]
                cursor.execute("""
                    INSERT INTO usbc_protocol_tests 
                    (usbc_inspection_id, protocol_name, supported, speed_mbps, power_delivery, max_power_w)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (usbc_inspection_id, protocol, True, speed, pd, power))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('device_detail', device_id=device_id))
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return f"Fehler beim Speichern: {str(e)}", 500

@app.route('/api/usbc-stats')
def usbc_stats():
    """API-Endpoint für USB-C Statistiken"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Datenbankverbindung fehlgeschlagen'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as count FROM devices WHERE type LIKE '%USB-C%'")
    total_devices = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM usbc_inspections")
    total_inspections = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT test_result, COUNT(*) as count 
        FROM usbc_inspections 
        GROUP BY test_result
    """)
    results = cursor.fetchall()
    
    cursor.execute("""
        SELECT protocol_name, COUNT(*) as count 
        FROM usbc_protocol_tests 
        WHERE supported = 1
        GROUP BY protocol_name 
        ORDER BY count DESC
    """)
    protocols = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'total_devices': total_devices,
        'total_inspections': total_inspections,
        'results': results,
        'protocols': protocols
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Benning Device Manager läuft auf http://0.0.0.0:5000")
    print("   + USB-C Kabel-Prüfung aktiviert 🔌")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
