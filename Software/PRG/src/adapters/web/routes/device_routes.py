"""Device Routes mit Response Handler - Verbesserte Error/Success Messages"""
from flask import Blueprint, request, jsonify
from src.core.domain.device import Device
from src.config.dependencies import container
from src.adapters.web.dto.device_dto import (
    create_device_request_from_json,
    update_device_request_from_json
)
from src.adapters.web.response_handler import ResponseHandler
from datetime import datetime

device_bp_v2 = Blueprint('devices_v2', __name__, url_prefix='/api/v2/devices')


def _clean_date_field(value):
    """Convert empty string to None for date fields with validation"""
    if not value or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except (ValueError, AttributeError):
            return None
    return value


@device_bp_v2.route('', methods=['GET'])
def list_devices():
    """Liste alle Devices auf"""
    try:
        devices = container.list_devices_usecase.execute()
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'action': 'LIST',
            'message': f'✅ {len(devices)} Device(s) gefunden',
            'data': [{
                'id': d.id,
                'customer': d.customer,
                'customer_device_id': d.customer_device_id,
                'name': d.name,
                'type': d.type,
                'location': d.location,
                'manufacturer': d.manufacturer,
                'serial_number': d.serial_number,
                'status': d.status
            } for d in devices],
            'count': len(devices)
        })
    except Exception as e:
        response = ResponseHandler.error_server(str(e))
        return jsonify(response), 500


@device_bp_v2.route('/<customer_device_id>', methods=['GET'])
def get_device(customer_device_id: str):
    """Hole ein einzelnes Device"""
    try:
        # Sanitize input
        customer_device_id = customer_device_id.strip() if customer_device_id else None
        
        if not customer_device_id:
            response = ResponseHandler.error_missing_required_field('customer_device_id')
            return jsonify(response), 400
        
        device = container.device_repository.get_by_customer_device_id(customer_device_id)
        if device:
            return jsonify({
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'action': 'GET',
                'message': f'✅ Device "{device.name}" gefunden',
                'device': {
                    'id': device.id,
                    'customer': device.customer,
                    'customer_device_id': device.customer_device_id,
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
        
        response = ResponseHandler.error_not_found(customer_device_id)
        return jsonify(response), 404
    except Exception as e:
        response = ResponseHandler.error_server(str(e))
        return jsonify(response), 500


@device_bp_v2.route('/next-id', methods=['GET'])
def get_next_customer_device_id():
    """Hole nächste customer_device_id"""
    try:
        customer = request.args.get('customer', '').strip()
        if not customer:
            response = ResponseHandler.error_missing_required_field('customer')
            return jsonify(response), 400
        
        next_id = container.device_repository.get_next_customer_device_id(customer)
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'action': 'GET_NEXT_ID',
            'message': f'✅ Nächste ID für "{customer}" generiert',
            'customer': customer,
            'next_id': next_id
        })
    except Exception as e:
        response = ResponseHandler.error_server(str(e))
        return jsonify(response), 500


@device_bp_v2.route('', methods=['POST'])
def create_device():
    """Erstelle ein neues Device"""
    try:
        data = request.json or {}
        
        # Validiere Request mit DTOs
        create_request, errors = create_device_request_from_json(data)
        if errors:
            response = ResponseHandler.error_validation(errors)
            return jsonify(response), 400
        
        device = Device(
            customer=create_request.customer,
            customer_device_id=create_request.customer_device_id,
            name=create_request.name,
            type=create_request.type,
            location=create_request.location,
            manufacturer=create_request.manufacturer,
            serial_number=create_request.serial_number,
            purchase_date=_clean_date_field(create_request.purchase_date),
            status=create_request.status,
            notes=create_request.notes
        )
        
        created = container.create_device_usecase.execute(device)
        
        response = ResponseHandler.success_create(
            device_id=created.id,
            customer_device_id=created.customer_device_id,
            customer=created.customer,
            name=created.name,
            device_type=created.type,
            additional_fields={
                'location': created.location,
                'manufacturer': created.manufacturer,
                'serial_number': created.serial_number,
                'status': created.status
            }
        )
        return jsonify(response), 201
    
    except ValueError as e:
        error_str = str(e)
        
        # Prüfe auf Duplicate Entry
        if "Duplicate entry" in error_str:
            response = ResponseHandler.format_error_message(error_str)
            return jsonify(response), 409
        
        response = ResponseHandler.error_validation([error_str])
        return jsonify(response), 400
    
    except Exception as e:
        error_str = str(e)
        
        # Prüfe auf Duplicate Entry
        if "Duplicate entry" in error_str:
            response = ResponseHandler.format_error_message(error_str)
            return jsonify(response), 409
        
        # Prüfe auf Datenbankverbindungsfehler
        if "Can't connect" in error_str or "connection" in error_str.lower():
            response = ResponseHandler.error_database_connection()
            return jsonify(response), 503
        
        response = ResponseHandler.error_server(error_str)
        return jsonify(response), 500


@device_bp_v2.route('/<customer_device_id>', methods=['PUT'])
def update_device(customer_device_id: str):
    """Aktualisiere ein Device"""
    try:
        # Sanitize customer_device_id
        customer_device_id = customer_device_id.strip() if customer_device_id else None
        if not customer_device_id:
            response = ResponseHandler.error_missing_required_field('customer_device_id')
            return jsonify(response), 400
        
        data = request.json or {}
        
        # Validiere Request mit DTOs
        update_request, errors = update_device_request_from_json(data)
        if errors:
            response = ResponseHandler.error_validation(errors)
            return jsonify(response), 400
        
        device = Device(
            customer_device_id=customer_device_id,
            customer=update_request.customer,
            name=update_request.name,
            type=update_request.type,
            location=update_request.location,
            manufacturer=update_request.manufacturer,
            serial_number=update_request.serial_number,
            purchase_date=_clean_date_field(update_request.purchase_date),
            status=update_request.status or 'active',
            notes=update_request.notes
        )
        
        updated = container.update_device_usecase.execute(device)
        
        # Sammle aktualisierte Felder
        updated_fields = {}
        if update_request.customer:
            updated_fields['customer'] = update_request.customer
        if update_request.name:
            updated_fields['name'] = update_request.name
        if update_request.type:
            updated_fields['type'] = update_request.type
        if update_request.location:
            updated_fields['location'] = update_request.location
        if update_request.manufacturer:
            updated_fields['manufacturer'] = update_request.manufacturer
        if update_request.serial_number:
            updated_fields['serial_number'] = update_request.serial_number
        if update_request.purchase_date:
            updated_fields['purchase_date'] = update_request.purchase_date
        if update_request.status:
            updated_fields['status'] = update_request.status
        if update_request.notes:
            updated_fields['notes'] = update_request.notes
        
        response = ResponseHandler.success_update(
            device_id=updated.id,
            customer_device_id=updated.customer_device_id,
            updated_fields=updated_fields
        )
        return jsonify(response)
    
    except ValueError as e:
        error_str = str(e)
        
        if "not found" in error_str.lower():
            response = ResponseHandler.error_not_found(customer_device_id)
            return jsonify(response), 404
        
        response = ResponseHandler.error_validation([error_str])
        return jsonify(response), 400
    
    except Exception as e:
        error_str = str(e)
        
        if "not found" in error_str.lower():
            response = ResponseHandler.error_not_found(customer_device_id)
            return jsonify(response), 404
        
        if "Duplicate entry" in error_str:
            response = ResponseHandler.format_error_message(error_str)
            return jsonify(response), 409
        
        response = ResponseHandler.error_server(error_str)
        return jsonify(response), 500


@device_bp_v2.route('/<customer_device_id>', methods=['DELETE'])
def delete_device(customer_device_id: str):
    """Lösche ein Device"""
    try:
        # Sanitize customer_device_id
        customer_device_id = customer_device_id.strip() if customer_device_id else None
        if not customer_device_id:
            response = ResponseHandler.error_missing_required_field('customer_device_id')
            return jsonify(response), 400
        
        container.delete_device_usecase.execute(customer_device_id)
        
        response = ResponseHandler.success_delete(customer_device_id)
        return jsonify(response)
    
    except ValueError as e:
        error_str = str(e)
        
        if "not found" in error_str.lower():
            response = ResponseHandler.error_not_found(customer_device_id)
            return jsonify(response), 404
        
        response = ResponseHandler.error_validation([error_str])
        return jsonify(response), 400
    
    except Exception as e:
        error_str = str(e)
        
        if "not found" in error_str.lower():
            response = ResponseHandler.error_not_found(customer_device_id)
            return jsonify(response), 404
        
        response = ResponseHandler.error_server(error_str)
        return jsonify(response), 500


@device_bp_v2.route('/health', methods=['GET'])
def health_check():
    """Health Check Endpoint"""
    try:
        from src.adapters.services.health_check_service import HealthCheckService
        from src.adapters.services.logger_service import LoggerService
        
        logger = LoggerService()
        health = HealthCheckService()
        
        health_status = health.full_health_check()
        
        logger.log_health_check(
            status=health_status.get('overall_status'),
            database_status=health_status.get('database', {}).get('status'),
            response_time_ms=health_status.get('database', {}).get('response_time_ms')
        )
        
        status_code = 200 if health_status.get('overall_status') == 'healthy' else 503
        return jsonify(health_status), status_code
    except Exception as e:
        return jsonify({
            'overall_status': 'unhealthy',
            'error': str(e)
        }), 503
