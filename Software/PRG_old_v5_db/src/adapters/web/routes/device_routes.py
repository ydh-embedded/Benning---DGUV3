"""Device Routes Adapter - FINAL mit ID Auto-Increment"""
from flask import Blueprint, request, jsonify
from src.core.domain.device import Device
from src.config.dependencies import container

device_bp = Blueprint('devices', __name__, url_prefix='/api/devices')

@device_bp.route('', methods=['GET'])
def list_devices():
    try:
        devices = container.list_devices_usecase.execute()
        return jsonify([{
            'id': d.id,
            'name': d.name,
            'type': d.type,
            'location': d.location,
            'manufacturer': d.manufacturer,
            'serial_number': d.serial_number,
            'status': d.status
        } for d in devices])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@device_bp.route('/<device_id>', methods=['GET'])
def get_device(device_id: str):
    try:
        device = container.get_device_usecase.execute(device_id)
        if device:
            return jsonify({
                'id': device.id,
                'name': device.name,
                'type': device.type,
                'location': device.location,
                'manufacturer': device.manufacturer,
                'serial_number': device.serial_number,
                'purchase_date': str(device.purchase_date) if device.purchase_date else None,
                'last_inspection': str(device.last_inspection) if device.last_inspection else None,
                'next_inspection': str(device.next_inspection) if device.next_inspection else None,
                'status': device.status,
                'notes': device.notes
            })
        return jsonify({'error': 'Device not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@device_bp.route('/next-id', methods=['GET'])
def get_next_id():
    """Get next device ID"""
    try:
        next_id = container.device_repository.get_next_id()
        return jsonify({'next_id': next_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@device_bp.route('', methods=['POST'])
def create_device():
    try:
        data = request.json
        device = Device(
            id=data.get('id'),
            name=data.get('name'),
            type=data.get('type'),
            location=data.get('location'),
            manufacturer=data.get('manufacturer'),
            serial_number=data.get('serial_number'),
            purchase_date=data.get('purchase_date'),
            status=data.get('status', 'active'),
            notes=data.get('notes')
        )
        created = container.create_device_usecase.execute(device)
        return jsonify({
            'id': created.id, 
            'message': 'Device created',
            'next_id': container.device_repository.get_next_id()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@device_bp.route('/<device_id>', methods=['PUT'])
def update_device(device_id: str):
    try:
        data = request.json
        device = Device(
            id=device_id,
            name=data.get('name'),
            type=data.get('type'),
            location=data.get('location'),
            manufacturer=data.get('manufacturer'),
            serial_number=data.get('serial_number'),
            purchase_date=data.get('purchase_date'),
            status=data.get('status', 'active'),
            notes=data.get('notes')
        )
        updated = container.update_device_usecase.execute(device)
        return jsonify({'message': 'Device updated', 'device': {
            'id': updated.id,
            'name': updated.name,
            'type': updated.type
        }})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@device_bp.route('/<device_id>', methods=['DELETE'])
def delete_device(device_id: str):
    try:
        container.delete_device_usecase.execute(device_id)
        return jsonify({'message': 'Device deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
