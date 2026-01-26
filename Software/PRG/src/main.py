"""
Benning Device Manager - Main Application
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Füge das Projektverzeichnis zum Python-Pfad hinzu BEVOR Module importiert werden
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from flask import Flask, render_template, request, jsonify, url_for
from src.config.settings import get_config
from src.config.dependencies import container
from src.adapters.web.routes.device_routes import device_bp
from src.adapters.services.qr_code_generator import QRCodeGenerator

# ✅ IMPORT PDF BLUEPRINT
try:
    from src.adapters.web.routes.pdf_export_route import pdf_bp
    PDF_ENABLED = True
except ImportError as e:
    print(f"⚠️  Warning: PDF export nicht verfügbar: {e}")
    PDF_ENABLED = False

def create_app():
    app = Flask(__name__, 
                template_folder=str(Path(__file__).parent.parent / 'templates'),
                static_folder=str(Path(__file__).parent.parent / 'static'))
    
    config = get_config()
    app.config.from_object(config)
    
    # Register Blueprints
    app.register_blueprint(device_bp)
    
    # ✅ REGISTER PDF BLUEPRINT (SICHER)
    if PDF_ENABLED:
        try:
            app.register_blueprint(pdf_bp)
            print("✅ PDF Export Routes registriert")
        except Exception as e:
            print(f"⚠️  Fehler beim Registrieren von PDF Routes: {e}")

    # ========================================================================
    # DASHBOARD - INDEX
    # ========================================================================
    @app.route('/')
    def index():
        """Dashboard mit Statistiken"""
        try:
            # Hole alle Geräte
            devices_list = container.list_devices_usecase.execute()
            
            # Berechne Statistiken
            total_devices = len(devices_list)
            
            # Zähle überfällige Prüfungen
            overdue = 0
            for device in devices_list:
                if device.next_inspection:
                    try:
                        next_insp = datetime.fromisoformat(str(device.next_inspection))
                        if next_insp < datetime.now():
                            overdue += 1
                    except:
                        pass
            
            # Zähle Prüfungen in letzten 30 Tagen
            recent_inspections = 0
            thirty_days_ago = datetime.now() - timedelta(days=30)
            for device in devices_list:
                if device.last_inspection:
                    try:
                        last_insp = datetime.fromisoformat(str(device.last_inspection))
                        if last_insp > thirty_days_ago:
                            recent_inspections += 1
                    except:
                        pass
            
            # Hole zuletzt hinzugefügte Geräte (sortiert nach ID)
            recent_devices = sorted(devices_list, key=lambda x: x.id, reverse=True)[:5]
            
            return render_template('index.html', 
                                 total_devices=total_devices,
                                 overdue=overdue,
                                 recent_inspections=recent_inspections,
                                 recent_devices=recent_devices)
        except Exception as e:
            print(f"Error loading dashboard: {e}")
            return render_template('index.html', 
                                 total_devices=0,
                                 overdue=0,
                                 recent_inspections=0,
                                 recent_devices=[],
                                 error=str(e))

    # ========================================================================
    # GERÄTELISTE
    # ========================================================================
    @app.route('/devices')
    def devices():
        """Geräteliste mit QR-Codes"""
        try:
            # Hole alle Geräte aus der Datenbank
            devices_list = container.list_devices_usecase.execute()
            
            # Generiere QR-Codes für jedes Gerät
            for device in devices_list:
                try:
                    # Generiere QR-Code basierend auf customer_device_id
                    qr_code_data = QRCodeGenerator.generate_qr_code(
                        device_id=device.customer_device_id,
                        customer=device.customer
                    )
                    # Konvertiere zu String für HTML
                    if qr_code_data:
                        device.qr_code = f"data:image/svg+xml;base64,{qr_code_data.decode('utf-8')}"
                    else:
                        device.qr_code = None
                except Exception as e:
                    print(f"Error generating QR code for {device.customer_device_id}: {e}")
                    device.qr_code = None
            
            return render_template('devices.html', devices=devices_list)
        except Exception as e:
            print(f"Error loading devices: {e}")
            return render_template('devices.html', devices=[], error=str(e))

    # ========================================================================
    # SCHNELLERFASSUNG
    # ========================================================================
    @app.route('/quick-add', methods=['GET', 'POST'])
    def quick_add():
        """Schnellerfassung für neue Geräte"""
        if request.method == 'GET':
            return render_template('quick_add.html')
        
        # POST request handling
        try:
            data = request.json or {}
            
            # Validiere erforderliche Felder
            if not data.get('customer'):
                return jsonify({'success': False, 'error': 'Kundenname erforderlich'}), 400
            if not data.get('name'):
                return jsonify({'success': False, 'error': 'Gerätename erforderlich'}), 400
            if not data.get('type'):
                return jsonify({'success': False, 'error': 'Gerätetyp erforderlich'}), 400
            
            # Erstelle Gerät
            from src.core.domain.device import Device
            device = Device(
                customer=data.get('customer'),
                name=data.get('name'),
                type=data.get('type'),
                location=data.get('location'),
                manufacturer=data.get('manufacturer'),
                serial_number=data.get('serial_number') or None,
                purchase_date=data.get('purchase_date') or None,
                notes=data.get('notes')
            )
            
            created = container.create_device_usecase.execute(device)
            return jsonify({
                'success': True,
                'device': {
                    'id': created.id,
                    'customer_device_id': created.customer_device_id,
                    'customer': created.customer,
                    'name': created.name,
                    'type': created.type
                },
                'message': 'Gerät erfolgreich erstellt'
            }), 201
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ========================================================================
    # USB-C PRÜFUNGEN
    # ========================================================================
    @app.route('/usbc-inspections')
    def usbc_inspections():
        """USB-C Inspektionen Übersicht"""
        try:
            devices_list = container.list_devices_usecase.execute()
            return render_template('usbc_inspections_list.html', devices=devices_list)
        except Exception as e:
            print(f"Error loading inspections: {e}")
            return render_template('usbc_inspections_list.html', devices=[], error=str(e))

    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error='Seite nicht gefunden'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error='Interner Fehler'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
