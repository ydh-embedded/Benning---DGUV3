
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
    # ANCHOR: DASHBOARD - INDEX
    # Hauptaufgabe: Dashboard mit Statistiken anzeigen
    # - Gesamtanzahl Geräte
    # - Überfällige Prüfungen
    # - Prüfungen in letzten 30 Tagen
    # - Geräte nach Status (aktiv, wartung, außer betrieb)
    # - Zuletzt hinzugefügte Geräte (Top 5)
    # - Interaktives Kreisdiagramm
    # ========================================================================
    @app.route('/')
    def index():
        """Dashboard mit Statistiken und Kreisdiagramm"""
        try:
            # Hole alle Geräte
            devices_list = container.list_devices_usecase.execute()
            
            # Berechne Statistiken
            total_devices = len(devices_list)
            
            # OPTIMIERUNG: Kombiniere alle Zählungen in einer einzigen Schleife
            # Zähle Prüfungen in letzten 3 Monaten
            overdue = 0
            recent_inspections = 0
            active_devices = 0
            maintenance_devices = 0
            retired_devices = 0
            three_months_ago = datetime.now() - timedelta(days=90)          
            for device in devices_list:
                # Zähle überfällige Prüfungen
                if device.next_inspection:
                    try:
                        next_insp = datetime.fromisoformat(str(device.next_inspection))
                        if next_insp < datetime.now():
                            overdue += 1
                    except:
                        pass
                
                # Zähle Prüfungen in letzten 3 Monaten
                if device.last_inspection:
                    try:
                        last_insp = datetime.fromisoformat(str(device.last_inspection))
                        if last_insp > three_months_ago:
                            recent_inspections += 1
                    except:
                        pass
                
                # Zähle Geräte nach Status
                if device.status == 'active':
                    active_devices += 1
                elif device.status == 'maintenance':
                    maintenance_devices += 1
                elif device.status == 'retired':
                    retired_devices += 1
            
            # Hole zuletzt hinzugefügte Geräte (sortiert nach ID)
            recent_devices = sorted(devices_list, key=lambda x: x.id, reverse=True)[:5]
            
            return render_template('index.html', 
                                 total_devices=total_devices,
                                 overdue=overdue,
                                 recent_inspections=recent_inspections,
                                 recent_devices=recent_devices,
                                 all_devices=devices_list,
                                 active_devices=active_devices,
                                 maintenance_devices=maintenance_devices,
                                 retired_devices=retired_devices)
        except Exception as e:
            print(f"Error loading dashboard: {e}")
            return render_template('index.html', 
                                 total_devices=0,
                                 overdue=0,
                                 recent_inspections=0,
                                 recent_devices=[],
                                 all_devices=[],
                                 active_devices=0,
                                 maintenance_devices=0,
                                 retired_devices=0,
                                 error=str(e))

    # ========================================================================
    # ANCHOR: GERÄTELISTE
    # Hauptaufgabe: Alle Geräte mit QR-Codes anzeigen
    # - Lade alle Geräte aus der Datenbank
    # - Generiere QR-Code für jedes Gerät
    # - Zeige in Tabellenformat mit Suchfunktion
    # ========================================================================
    @app.route('/devices')
    def devices():
        """Geräteliste mit QR-Codes und Suchfunktion"""
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
    # ANCHOR: GERÄTEDETAILS
    # Hauptaufgabe: Detaillierte Informationen zu einem spezifischen Gerät
    # - Lade Gerätedaten nach ID
    # - Generiere QR-Code
    # - Zeige Inspektionshistorie
    # ========================================================================
    @app.route('/device/<int:device_id>')
    def device_detail(device_id):
        """Gerätedetails mit QR-Code und Inspektionshistorie"""
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
    # ANCHOR: GERÄT LÖSCHEN (DELETE ENDPOINT)
    # Hauptaufgabe: Gerät und alle zugehörigen Daten löschen
    # - DELETE: Lösche Gerät und alle Inspektionsdaten
    # - Bestätigung erforderlich
    # ========================================================================
    @app.route('/device/<int:device_id>/delete', methods=['DELETE'])
    def delete_device(device_id):
        """API Endpoint zum Löschen eines Geräts mit allen zugehörigen Daten"""
        try:
            # Hole das Gerät
            device = container.device_repository.get_by_id(device_id)
            
            if not device:
                return jsonify({
                    'status': 'error',
                    'message': 'Gerät nicht gefunden'
                }), 404
            
            # Speichere Gerätename für die Antwort
            device_name = device.name
            device_id_str = device.customer_device_id
            
            # TODO: Lösche alle zugehörigen Inspektionsdaten
            # container.inspection_repository.delete_by_device_id(device_id)
            
            # TODO: Lösche das Gerät
            # container.device_repository.delete(device_id)
            
            print(f"Gerät gelöscht: {device_name} ({device_id_str})")
            
            return jsonify({
                'status': 'success',
                'message': f'Gerät {device_name} wurde erfolgreich gelöscht',
                'device_id': device_id,
                'device_name': device_name
            }), 200
            
        except Exception as e:
            print(f"Fehler beim Löschen des Geräts {device_id}: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Fehler beim Löschen des Geräts',
                'details': str(e)
            }), 500


    # ========================================================================
    # ANCHOR: SCHNELLERFASSUNG
    # Hauptaufgabe: Schnelle Erfassung neuer Geräte
    # - GET: Zeige Erfassungsformular mit nächster ID
    # - POST: Speichere neues Gerät in Datenbank
    # - Automatische ID-Generierung nach Kundennamen
    # ========================================================================
    @app.route('/quick-add', methods=['GET', 'POST'])
    def quick_add():
        """Schnellerfassung für neue Geräte mit automatischer ID"""
        if request.method == 'POST':
            return jsonify({'status': 'success'})
        
        try:
            # Hole nächste ID für Standard-Kunden
            next_id = container.device_repository.get_next_customer_device_id('Default')
            # Generiere URL zur USB-C Inspektionen Seite
            usbc_inspections_url = url_for('usbc_inspections')
            return render_template('quick_add.html', next_id=next_id, usbc_inspections_url=usbc_inspections_url)
        except Exception as e:
            usbc_inspections_url = url_for('usbc_inspections')
            return render_template('quick_add.html', next_id='Default-00001', error=str(e), usbc_inspections_url=usbc_inspections_url)

    # ========================================================================
    # ANCHOR: GERÄT HINZUFÜGEN (API ENDPOINT)
    # Hauptaufgabe: Neues Gerät mit optionalen USB-Inspektionsdaten speichern
    # - POST: Speichere neues Gerät und optionale USB-Inspektion
    # - Aktualisiere Gerätestatus basierend auf USB-Inspektionsergebnis
    # ========================================================================
    @app.route('/device/add', methods=['POST'])
    def add_device():
        """API Endpoint zum Hinzufügen eines neuen Geräts mit optionalen USB-Inspektionsdaten"""
        try:
            # Hole JSON Daten aus Request
            data = request.get_json()
            
            # Validiere erforderliche Felder
            required_fields = ['customer', 'name', 'type']
            if not all(field in data for field in required_fields):
                return jsonify({
                    'status': 'error',
                    'message': 'Erforderliche Felder fehlen: customer, name, type'
                }), 400
            
            # TODO: Speichere Gerät in Datenbank
            # device = container.create_device_usecase.execute({
            #     'customer': data['customer'],
            #     'name': data['name'],
            #     'type': data['type'],
            #     'location': data.get('location'),
            #     'manufacturer': data.get('manufacturer'),
            #     'serial_number': data.get('serial_number'),
            #     'purchase_date': data.get('purchase_date'),
            #     'last_inspection': data.get('last_inspection'),
            #     'next_inspection': data.get('next_inspection'),
            #     'status': data.get('status', 'active'),
            #     'notes': data.get('notes')
            # })
            
            # Bestimme Gerätestatus basierend auf USB-Inspektionsergebnis
            device_status = data.get('status', 'active')
            
            # Wenn USB-Kabel Typ und Testergebnis vorhanden
            if data.get('type') == 'USB-Kabel' and data.get('test_result'):
                if data['test_result'] == 'bestanden':
                    device_status = 'active'
                else:  # nicht_bestanden, verloren, nicht_vorhanden
                    device_status = 'maintenance'
            
            # TODO: Speichere USB-Inspektionsdaten wenn vorhanden
            # if data.get('cable_type') and data.get('test_result'):
            #     inspection = container.create_inspection_usecase.execute({
            #         'device_id': device.id,
            #         'cable_type': data['cable_type'],
            #         'test_result': data['test_result'],
            #         'internal_resistance': data.get('internal_resistance'),
            #         'emarker_active': data.get('emarker_active'),
            #         'notes': data.get('inspection_notes')
            #     })
            
            print(f"Gerät erstellt: {data['name']} (Typ: {data['type']})")
            if data.get('cable_type'):
                print(f"USB-Inspektion: {data['cable_type']} - {data['test_result']}")
            
            return jsonify({
                'status': 'success',
                'message': 'Gerät erfolgreich gespeichert',
                'device_status': device_status
            }), 201
            
        except Exception as e:
            print(f"Fehler beim Speichern des Geräts: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Fehler beim Speichern des Geräts',
                'details': str(e)
            }), 500


    # ========================================================================
    # ANCHOR: USB-C INSPEKTIONEN LISTE
    # Hauptaufgabe: Übersicht aller USB-C Kabel-Prüfungen
    # - Zeige alle durchgeführten Inspektionen
    # - Filtermöglichkeiten nach Status und Datum
    # - Link zu Inspektionsdetails
    # ========================================================================
    @app.route('/usbc-inspections')
    def usbc_inspections():
        """USB-C Inspektionen Übersicht mit Filterfunktion"""
        try:
            # Placeholder: Später mit echten Inspektionsdaten
            inspections = []
            return render_template('usbc_inspections_list.html', inspections=inspections)
        except Exception as e:
            return render_template('usbc_inspections_list.html', inspections=[], error=str(e))

    # ========================================================================
    # ANCHOR: USB-C INSPEKTIONEN FÜR SPEZIFISCHES GERÄT
    # Hauptaufgabe: Inspektionsformular für ein Gerät
    # - GET: Zeige Inspektionsformular
    # - POST: Speichere Inspektionsergebnis
    # - Verknüpfung mit Gerätedaten
    # ========================================================================
    @app.route('/device/<int:device_id>/usbc-inspection', methods=['GET', 'POST'])
    def device_usbc_inspection(device_id):
        """USB-C Inspektionsformular für ein spezifisches Gerät"""
        try:
            device = container.device_repository.get_by_id(device_id)
            if device:
                if request.method == 'POST':
                    try:
                        # Hole Inspektionsdaten aus dem Request
                        inspection_data = request.get_json()
                        
                        # Validiere erforderliche Felder
                        required_fields = ['cable_type', 'test_result']
                        if not all(field in inspection_data for field in required_fields):
                            return jsonify({
                                'status': 'error',
                                'message': 'Erforderliche Felder fehlen: cable_type, test_result'
                            }), 400
                        
                        # Validiere test_result Werte
                        valid_results = ['bestanden', 'nicht_bestanden', 'verloren', 'nicht_vorhanden']
                        if inspection_data['test_result'] not in valid_results:
                            return jsonify({
                                'status': 'error',
                                'message': f'Ungültiges Inspektionsergebnis. Erlaubte Werte: {valid_results}'
                            }), 400
                        
                        # TODO: Speichere Inspektionsdaten in Datenbank
                        # inspection = container.create_inspection_usecase.execute(inspection_data, device_id)
                        
                        # Bestimme neuen Gerätstatus basierend auf Inspektionsergebnis
                        new_device_status = 'active' if inspection_data['test_result'] == 'bestanden' else 'maintenance'
                        
                        # TODO: Aktualisiere Gerätstatus
                        # device.status = new_device_status
                        # device.last_inspection = datetime.now()
                        # container.device_repository.update(device)
                        
                        print(f"Inspektion für Gerät {device_id} erstellt: {inspection_data['test_result']}")
                        print(f"Gerätstatus aktualisiert zu: {new_device_status}")
                        
                        return jsonify({
                            'status': 'success',
                            'message': 'Inspektion erfolgreich gespeichert',
                            'device_id': device_id,
                            'device_status_updated': new_device_status,
                            'inspection_result': inspection_data['test_result']
                        }), 201
                    except Exception as e:
                        print(f"Fehler beim Speichern der Inspektion: {e}")
                        return jsonify({
                            'status': 'error',
                            'message': str(e)
                        }), 400
                
                return render_template('usbc_inspection.html', device=device)
            else:
                return render_template('error.html', error='Device nicht gefunden'), 404
        except Exception as e:
            print(f"Error in device_usbc_inspection: {e}")
            return render_template('error.html', error=str(e)), 500

    # ========================================================================
    # ANCHOR: USB-C INSPEKTIONEN DETAIL FÜR SPEZIFISCHES GERÄT
    # Hauptaufgabe: Detaillierte Inspektionsergebnisse anzeigen
    # - Lade Inspektionsdaten nach ID
    # - Zeige Inspektionsergebnisse und Bilder
    # - Ermögliche Bearbeitung und Löschung
    # ========================================================================
    @app.route('/device/<int:device_id>/usbc-inspection/<int:inspection_id>')
    def device_usbc_inspection_detail(device_id, inspection_id):
        """USB-C Inspektionsdetails für ein spezifisches Gerät"""
        try:
            device = container.device_repository.get_by_id(device_id)
            if device:
                # TODO: Hole Inspektionsdaten
                # Später: inspection = container.get_inspection_usecase.execute(inspection_id)
                inspection = {
                    'id': inspection_id,
                    'device_id': device_id,
                    'inspection_date': datetime.now(),
                    'cable_type': 'USB-C',
                    'test_result': 'bestanden',
                    'internal_resistance': 0.5,
                    'emarker_active': True,
                    'notes': 'Beispiel Inspektionsdaten'
                }
                return render_template('usbc_inspection_detail.html', device=device, inspection=inspection)
            else:
                return render_template('error.html', error='Device nicht gefunden'), 404
        except Exception as e:
            print(f"Error in device_usbc_inspection_detail: {e}")
            return render_template('error.html', error=str(e)), 500
    
    # ========================================================================
    # ANCHOR: ALLE USB-C INSPEKTIONEN FÜR EIN GERÄT
    # Hauptaufgabe: Inspektionsverlauf eines Geräts anzeigen
    # - Zeige alle Inspektionen eines Geräts
    # - Sortiert nach Datum (neueste zuerst)
    # - Link zu Inspektionsdetails
    # ========================================================================
    @app.route('/device/<int:device_id>/usbc-inspections')
    def device_usbc_inspections_list(device_id):
        """Alle USB-C Inspektionen für ein spezifisches Gerät"""
        try:
            device = container.device_repository.get_by_id(device_id)
            if device:
                # TODO: Hole alle Inspektionen für dieses Gerät
                # Später: inspections = container.list_inspections_usecase.execute(device_id)
                inspections = [
                    {
                        'id': 1,
                        'inspection_date': datetime.now() - timedelta(days=5),
                        'cable_type': 'USB-C',
                        'test_result': 'bestanden',
                        'internal_resistance': 0.5,
                        'emarker_active': True
                    }
                ]
                return render_template('device_usbc_inspections_list.html', device=device, inspections=inspections)
            else:
                return render_template('error.html', error='Gerät nicht gefunden'), 404
        except Exception as e:
            print(f"Fehler beim Laden der Inspektionsliste: {e}")
            return render_template('error.html', error=str(e)), 500

    # ========================================================================
    # ANCHOR: HEALTH CHECK ENDPOINTS
    # Hauptaufgabe: Überprüfung der Anwendungsverfügbarkeit
    # - /health: Allgemeiner Health Check
    # - /api/health: API-spezifischer Health Check
    # ========================================================================
    @app.route('/health', methods=['GET'])
    def health():
        """Health Check für Anwendungsverfügbarkeit"""
        return {'status': 'ok'}, 200

    @app.route('/api/health', methods=['GET'])
    def api_health():
        """Health Check für API-Verfügbarkeit"""
        return {'status': 'ok'}, 200

    # ========================================================================
    # ANCHOR: ERROR HANDLERS
    # Hauptaufgabe: Fehlerbehandlung und Benutzerfreundliche Fehlermeldungen
    # - 404: Seite nicht gefunden
    # - 500: Server-Fehler
    # ========================================================================
    @app.errorhandler(404)
    def not_found(error):
        """404 Error Handler - Seite nicht gefunden"""
        return render_template('error.html', error='Seite nicht gefunden'), 404

    @app.errorhandler(500)
    def server_error(error):
        """500 Error Handler - Server-Fehler"""
        return render_template('error.html', error='Server-Fehler'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
