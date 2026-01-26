
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

def create_app():
    app = Flask(__name__, 
                template_folder=str(Path(__file__).parent.parent / 'templates'),
                static_folder=str(Path(__file__).parent.parent / 'static'))
    
    config = get_config()
    app.config.from_object(config)
    app.register_blueprint(device_bp)

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
    # GERÄTEDETAILS
    # ========================================================================
    @app.route('/device/<int:device_id>')
    def device_detail(device_id):
        """Gerätedetails mit QR-Code"""
        try:
            device = container.device_repository.get_by_id(device_id)
            if device:
                # Generiere QR-Code
                qr_code_data = QRCodeGenerator.generate_qr_code(
                    device_id=device.customer_device_id,
                    customer=device.customer
                )
                if qr_code_data:
                    device.qr_code = f"data:image/svg+xml;base64,{qr_code_data.decode('utf-8')}"
                else:
                    device.qr_code = None
                
                # Hole Inspektionen (placeholder)
                inspections = []
                return render_template('device_detail.html', device=device, inspections=inspections)
            else:
                return render_template('error.html', error='Device nicht gefunden'), 404
        except Exception as e:
            return render_template('error.html', error=str(e)), 500

    # ========================================================================
    # SCHNELLERFASSUNG
    # ========================================================================
    @app.route('/quick-add', methods=['GET', 'POST'])
    def quick_add():
        """Schnellerfassung für neue Geräte"""
        if request.method == 'POST':
            return jsonify({'status': 'success'})
        
        try:
            # Hole nächste ID für Standard-Kunden
            next_id = container.device_repository.get_next_customer_device_id('Default')
            return render_template('quick_add.html', next_id=next_id)
        except Exception as e:
            return render_template('quick_add.html', next_id='Default-00001', error=str(e))

    # ========================================================================
    # USB-C INSPEKTIONEN LISTE
    # ========================================================================
    @app.route('/usbc-inspections')
    def usbc_inspections():
        """USB-C Inspektionen Übersicht"""
        try:
            # Placeholder: Später mit echten Inspektionsdaten
            inspections = []
            return render_template('usbc_inspections_list.html', inspections=inspections)
        except Exception as e:
            return render_template('usbc_inspections_list.html', inspections=[], error=str(e))

    # ========================================================================
    # USB-C INSPEKTIONEN DETAIL
    # ========================================================================
    @app.route('/usbc-inspection/<int:inspection_id>')
    def usbc_inspection_detail(inspection_id):
        """USB-C Inspektionsdetails"""
        try:
            # Placeholder: Später mit echten Inspektionsdaten
            inspection = {}
            device = {}
            return render_template('usbc_inspection.html', inspection=inspection, device=device)
        except Exception as e:
            return render_template('error.html', error=str(e)), 500

    # ========================================================================
    # HEALTH CHECK ENDPOINTS
    # ========================================================================
    @app.route('/health', methods=['GET'])
    def health():
        """Health Check"""
        return {'status': 'ok'}, 200

    @app.route('/api/health', methods=['GET'])
    def api_health():
        """API Health Check"""
        return {'status': 'ok'}, 200

    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================
    @app.errorhandler(404)
    def not_found(error):
        """404 Error Handler"""
        return render_template('error.html', error='Seite nicht gefunden'), 404

    @app.errorhandler(500)
    def server_error(error):
        """500 Error Handler"""
        return render_template('error.html', error='Server-Fehler'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
