"""Device Routes Adapter - FINAL mit Customer-basierter ID und konsistenten Responses"""
from flask import Blueprint, request, jsonify
from src.core.domain.device import Device
from src.config.dependencies import container

device_bp = Blueprint('devices', __name__, url_prefix='/api/devices')

@device_bp.route('', methods=['GET'])
def list_devices():
    try:
        devices = container.list_devices_usecase.execute()
        return jsonify({
            'success': True,
            'data': [{
                'id': d.id,
                'customer': d.customer,
                'device_id': d.device_id,
                'name': d.name,
                'type': d.type,
                'location': d.location,
                'manufacturer': d.manufacturer,
                'serial_number': d.serial_number,
                'status': d.status
            } for d in devices]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@device_bp.route('/<device_id>', methods=['GET'])
def get_device(device_id: str):
    try:
        device = container.device_repository.get_by_device_id(device_id)
        if device:
            return jsonify({
                'success': True,
                'device': {
                    'id': device.id,
                    'customer': device.customer,
                    'device_id': device.device_id,
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
                }
            })
        return jsonify({'success': False, 'error': 'Device not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@device_bp.route('/next-id', methods=['GET'])
def get_next_id():
    """Get next device ID"""
    try:
        customer = request.args.get('customer', '')
        if not customer:
            return jsonify({'success': False, 'error': 'Customer parameter required'}), 400
        
        next_id = container.device_repository.get_next_id(customer)
        return jsonify({
            'success': True,
            'next_id': next_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@device_bp.route('', methods=['POST'])
def create_device():
    try:
        data = request.json
        device = Device(
            id=data.get('id'),
            customer=data.get('customer'),
            device_id=data.get('device_id'),
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
            'success': True,
            'device': {
                'id': created.id,
                'device_id': created.device_id,
                'customer': created.customer,
                'name': created.name,
                'type': created.type
            },
            'message': 'Device created successfully'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@device_bp.route('/<device_id>', methods=['PUT'])
def update_device(device_id: str):
    try:
        data = request.json
        device = Device(
            device_id=device_id,
            customer=data.get('customer'),
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
        return jsonify({
            'success': True,
            'device': {
                'id': updated.id,
                'device_id': updated.device_id,
                'customer': updated.customer,
                'name': updated.name,
                'type': updated.type
            },
            'message': 'Device updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@device_bp.route('/<device_id>', methods=['DELETE'])
def delete_device(device_id: str):
    try:
        container.delete_device_usecase.execute(device_id)
        return jsonify({
            'success': True,
            'message': 'Device deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    

# ============================================================================
# HEALTH CHECK ROUTE
# ============================================================================
@device_bp.route('/health', methods=['GET'])
def health_check():
    """Überprüft den Gesundheitsstatus der Anwendung"""
    try:
        from src.adapters.services.health_check_service import HealthCheckService
        from src.adapters.services.logger_service import LoggerService
        
        logger = LoggerService()
        health = HealthCheckService()
        
        # Führe Health Check aus
        health_status = health.full_health_check()
        
        # Logge den Health Check
        logger.log_health_check(
            status=health_status.get('overall_status'),
            database_status=health_status.get('database', {}).get('status'),
            response_time_ms=health_status.get('database', {}).get('response_time_ms')
        )
        
        # Gebe Status zurück
        status_code = 200 if health_status.get('overall_status') == 'healthy' else 503
        return jsonify(health_status), status_code
    except Exception as e:
        logger.error("Health check failed", exception=e)
        return jsonify({
            'overall_status': 'unhealthy',
            'error': str(e)
        }), 503
