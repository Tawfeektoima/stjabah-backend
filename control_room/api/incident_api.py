"""API handlers for Control Room incident endpoints"""

from flask import Blueprint, request, jsonify
import logging

from control_room.service.incident_service import IncidentService
from control_room.model.incident import Incident

logger = logging.getLogger(__name__)

control_room_bp = Blueprint('control_room', __name__)

def init_control_room_api(incident_service: IncidentService):
    """Initialize the Control Room API with service dependencies"""
    control_room_bp.incident_service = incident_service
    return control_room_bp

@control_room_bp.route('/incidents/<incident_id>', methods=['GET'])
def get_incident_by_id(incident_id: str):
    try:
        incident = control_room_bp.incident_service.get_incident_by_id(incident_id)

        if incident is None:
            return jsonify({
                'error': 'Incident not found',
                'incident_id': incident_id
            }), 404
        
        return jsonify(incident.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error retrieving incident {incident_id}: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500
    
@control_room_bp.route('/incidents', methods=['POST'])
def create_incident():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'error': 'Invalid JSON payload'
            }), 400
        
        if 'x' not in data:
            return jsonify({
                'error': 'Missing x coordinate'
            }), 400
        
        if not isinstance(data['x'], (int, float)):
            return jsonify({
                'error': 'Invalid x coordinate'
            }), 400

        if 'y' not in data:
            return jsonify({
                'error': 'Missing y coordinate'
            }), 400
        
        if not isinstance(data['y'], (int, float)):
            return jsonify({
                'error': 'Invalid y coordinate'
            }), 400
        
        incident = control_room_bp.incident_service.create_incident(data['x'], data['y'])
        return jsonify(incident.to_dict()), 201

    except Exception as e:
        logger.error(f"Error creating incident: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500