"""Main application entry point for Emergency Response System"""

from flask import Flask
import logging
from control_room.api.incident_api import control_room_bp, init_control_room_api
from control_room.service.incident_service import IncidentService
from control_room.repository.in_memory_incident_repository import InMemoryIncidentRepository
from communication import CommunicationChannel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Initialize repositories
    logger.info("Initializing repositories...")
    # TODO: Initailize persistent incident repository (database, file, etc.)

    logger.info("Initializing communication channel...")
    incident_repository = InMemoryIncidentRepository()
    communication_channel = None

    logger.info("Initializing services...")
    incident_service = IncidentService(incident_repository=incident_repository, communication_channel=communication_channel)
    
    logger.info("Registering blueprints...")
    # TODO:Initialize and register blueprints
    control_room_bp = init_control_room_api(incident_service)
    # ert_bp = init_ert_api(unit_service)

    app.register_blueprint(control_room_bp, url_prefix='/cr')
    # app.register_blueprint(ert_bp, url_prefix='/ert')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'emergency-response-system'}, 200
    
    logger.info("Application initialized successfully")
    return app

if __name__ == '__main__':
    app = create_app()
    
    logger.info("Starting Emergency Response System...")
    logger.info("Control Room API: /cr/incidents")
    logger.info("ERT API: /ert/units/<unit_id>/...")
    logger.info("Health check: /health")
    
    # Run the Flask application
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=True
    )
