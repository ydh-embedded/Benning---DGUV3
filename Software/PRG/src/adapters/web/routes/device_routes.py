"""
Device Routes - Flask Web Adapter
"""
from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from ...core.usecases.device_usecases import (
    GetDeviceUseCase,
    ListDevicesUseCase,
    CreateDeviceUseCase,
    GetDevicesDueForInspectionUseCase
)

device_bp = Blueprint('devices', __name__, url_prefix='/devices')


class DeviceRoutes:
    """Device Route Handler"""
    
    def __init__(self, 
                 get_device_uc: GetDeviceUseCase,
                 list_devices_uc: ListDevicesUseCase,
                 create_device_uc: CreateDeviceUseCase,
                 get_due_uc: GetDevicesDueForInspectionUseCase):
        self.get_device_uc = get_device_uc
        self.list_devices_uc = list_devices_uc
        self.create_device_uc = create_device_uc
        self.get_due_uc = get_due_uc
        self._register_routes()
    
    def _register_routes(self):
        """Registriere Routes"""
        device_bp.route('/', methods=['GET'])(self.list_devices)
        device_bp.route('/<device_id>', methods=['GET'])(self.get_device)
        device_bp.route('', methods=['POST'])(self.create_device)
    
    def list_devices(self):
        """GET /devices - Alle Geräte auflisten"""
        try:
            devices = self.list_devices_uc.execute()
            return jsonify([{
                'id': str(d.id),
                'name': d.name,
                'type': d.type,
                'location': d.location,
                'status': d.status,
                'next_inspection': d.next_inspection.isoformat() if d.next_inspection else None
            } for d in devices])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def get_device(self, device_id: str):
        """GET /devices/<device_id> - Gerät abrufen"""
        try:
            device = self.get_device_uc.execute(device_id)
            return jsonify({
                'id': str(device.id),
                'name': device.name,
                'type': device.type,
                'location': device.location,
                'manufacturer': device.manufacturer,
                'serial_number': device.serial_number,
                'purchase_date': device.purchase_date.isoformat() if device.purchase_date else None,
                'last_inspection': device.last_inspection.isoformat() if device.last_inspection else None,
                'next_inspection': device.next_inspection.isoformat() if device.next_inspection else None,
                'status': device.status,
                'notes': device.notes
            })
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def create_device(self):
        """POST /devices - Neues Gerät erstellen"""
        try:
            data = request.json
            device = self.create_device_uc.execute(data)
            return jsonify({
                'id': str(device.id),
                'message': 'Gerät erfolgreich erstellt'
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400
