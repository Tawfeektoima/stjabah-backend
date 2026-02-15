"""API handlers for Control Room incident endpoints"""
from flask import Blueprint, request, jsonify
import logging
import asyncio
from control_room.service.incident_service import IncidentService

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

@control_room_bp.route('/incidents', methods=['GET'])
def list_incidents():
    try:
        incidents = control_room_bp.incident_service.get_all_incidents()
        incidents_data = [incident.to_dict() for incident in incidents]
        
        return jsonify(incidents_data), 200
        
    except Exception as e:
        logger.error(f"Error listing incidents: {str(e)}")
    
@control_room_bp.route('/incidents', methods=['POST'])
def create_incident():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'error': 'Invalid JSON payload'
            }), 400
        
        # Give error if the user try to create a new incident while there is still a one that is not resolved
        open_incidents = control_room_bp.incident_service.get_open_incidents()
        if len(open_incidents) > 0:
            return jsonify({
                'error': 'There is already an open incident. Please resolve it before creating a new one.',
                'open_incidents': [incident.to_dict() for incident in open_incidents]
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
    
@control_room_bp.route('/incidents/<incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    """
    Delete an incident from the system
    
    Args:
        incident_id: The unique identifier of the incident to delete
    
    Returns:
        200: Incident deleted successfully with success message
        404: Incident not found with error message
    """
    deleted = control_room_bp.incident_service.delete_incident(incident_id)
    
    if not deleted:
        return jsonify({"error": "Incident not found"}), 404
    
    return jsonify({"message": "Incident deleted successfully"}), 200

@control_room_bp.route('/incidents/<incident_id>', methods=['PUT'])
def update_incident(incident_id):
    """
    Update incident coordinates
    Args:
        incident_id: The unique identifier of the incident to update
    Returns:
        200: Incident updated successfully with updated incident data
    """

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
    
    try:
        incident = control_room_bp.incident_service.update_incident(incident_id, data['x'], data['y'])
        return jsonify(incident.to_dict()), 200

    except Exception as e:
        logger.error(f"Error updating incident {incident_id}: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500
    
@control_room_bp.route('/incidents/<incident_id>/dispatch', methods=['POST'])
def dispatch_incident(incident_id):
    """
    Dispatch an incident to the Emergency Response Team (ERT)
    Following Golden Rule: API calls Service Layer method which handles WebSocket publishing
    
    Args:
        incident_id: The unique identifier of the incident to dispatch
    
    Returns:
        200: Incident dispatched successfully with incident data
        404: Incident not found with error message
        500: Internal server error
    """
    try:
        # First get the incident to verify it exists
        incident = control_room_bp.incident_service.get_incident_by_id(incident_id)
        
        if incident is None:
            return jsonify({
                'error': 'Incident not found',
                'incident_id': incident_id
            }), 404
        
        # Run the async dispatch method
        # Create a new event loop for this request
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(
                control_room_bp.incident_service.dispatch_incident(incident_id)
            )
            loop.close()
        except RuntimeError:
            # If there's already an event loop, use it
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we need to use a different approach
                # This shouldn't happen in normal Flask operation
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, 
                        control_room_bp.incident_service.dispatch_incident(incident_id))
                    success = future.result()
            else:
                success = loop.run_until_complete(
                    control_room_bp.incident_service.dispatch_incident(incident_id)
                )
        
        if success:
            return jsonify({
                'message': 'Incident dispatched successfully',
                'incident': incident.to_dict()
            }), 200
        else:
            return jsonify({
                'error': 'Failed to dispatch incident'
            }), 500
    
    except Exception as e:
        logger.error(f"Error dispatching incident {incident_id}: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500