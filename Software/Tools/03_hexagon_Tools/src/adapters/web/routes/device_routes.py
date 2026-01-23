"""Device Routes Adapter"""
from flask import Blueprint, request, jsonify
from src.core.domain.device import Device
from src.core.usecases.device_usecases import (
    GetDeviceUseCase, ListDevicesUseCase, CreateDeviceUseCase,
    UpdateDeviceUseCase, DeleteDeviceUseCase
)

device_bp = Blueprint('devices', __name__, url_prefix='/api/devices')

@device_bp.route('', methods=['GET'])
def list_devices(list_usecase: ListDevicesUseCase):
    try:
        devices = list_usecase.execute()
        return jsonify([{'id': d.id, 'name': d.name, 'serial_number': d.serial_number, 'device_type': d.device_type} for d in devices])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@device_bp.route('/<int:device_id>', methods=['GET'])
def get_device(device_id: int, get_usecase: GetDeviceUseCase):
    try:
        device = get_usecase.execute(device_id)
        if device:
            return jsonify({'id': device.id, 'name': device.name, 'serial_number': device.serial_number, 'device_type': device.device_type, 'manufacturer': device.manufacturer, 'model': device.model, 'description': device.description})
        return jsonify({'error': 'Device not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@device_bp.route('', methods=['POST'])
def create_device(create_usecase: CreateDeviceUseCase):
    try:
        data = request.json
        device = Device(name=data.get('name'), device_type=data.get('device_type'), serial_number=data.get('serial_number'), manufacturer=data.get('manufacturer'), model=data.get('model'), description=data.get('description'))
        created = create_usecase.execute(device)
        return jsonify({'id': created.id, 'message': 'Device created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@device_bp.route('/<int:device_id>', methods=['PUT'])
def update_device(device_id: int, update_usecase: UpdateDeviceUseCase):
    try:
        data = request.json
        device = Device(id=device_id, name=data.get('name'), device_type=data.get('device_type'), serial_number=data.get('serial_number'), manufacturer=data.get('manufacturer'), model=data.get('model'), description=data.get('description'))
        update_usecase.execute(device)
        return jsonify({'message': 'Device updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@device_bp.route('/<int:device_id>', methods=['DELETE'])
def delete_device(device_id: int, delete_usecase: DeleteDeviceUseCase):
    try:
        delete_usecase.execute(device_id)
        return jsonify({'message': 'Device deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
