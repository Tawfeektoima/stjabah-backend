"""Main application entry point for Emergency Response System"""

from flask import Flask
import logging

# Control Room imports
from control_room.api.incident_api import init_control_room_api
from control_room.service.incident_service import IncidentService
from control_room.repository.in_memory_incident_repository import InMemoryIncidentRepository
from control_room.repository.incident_repository import IncidentRepository

# ERT imports
from ert.api.unit_api import init_ert_api
from ert.service.unit_service import UnitService
from ert.service.path_service import PathService
from ert.repository.unit_repository import UnitRepository

# Communication imports
from communication.channel import CommunicationChannel
from communication.message import Message

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
    
    # Choose repository implementation (similar to Spring Boot @Primary/@Bean)
    # You can switch between implementations here:
    # - InMemoryIncidentRepository: For testing/development
    # - SQLIncidentRepository: For production (when implemented)
    incident_repository: IncidentRepository = InMemoryIncidentRepository()
    
    unit_repository = UnitRepository()
    
    # Initialize communication channel
    # TODO: Implement concrete communication channel (WebSocket, polling, SIM, etc.)
    # For now, using a placeholder - replace with actual implementation
    logger.info("Initializing communication channel...")
    communication_channel = CommunicationChannelImpl()
    
    # Initialize services
    logger.info("Initializing services...")
    path_service = PathService()
    
    incident_service = IncidentService(
        incident_repository=incident_repository,
        communication_channel=communication_channel
    )
    
    unit_service = UnitService(
        unit_repository=unit_repository,
        path_service=path_service,
        communication_channel=communication_channel
    )
    
    # Initialize and register blueprints
    logger.info("Registering blueprints...")
    control_room_bp = init_control_room_api(incident_service)
    ert_bp = init_ert_api(unit_service)
    
    app.register_blueprint(control_room_bp, url_prefix='/cr')
    app.register_blueprint(ert_bp, url_prefix='/ert')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'emergency-response-system'}, 200
    
    logger.info("Application initialized successfully")
    return app


class CommunicationChannelImpl(CommunicationChannel):
    """
    Placeholder implementation of CommunicationChannel.
    Replace this with actual implementation (WebSocket, polling, SIM, etc.)
    """
    
    def __init__(self):
        logger.warning("Using placeholder CommunicationChannel - replace with actual implementation")
        self.subscribers = {}
    
    def send_message(self, recipient_id: str, message):
        """Send a message to a recipient"""
        logger.info(f"Sending message to {recipient_id}: {message.message_type}")
        # TODO: Implement actual message sending
        pass
    
    def broadcast_message(self, recipient_ids: list, message):
        """Broadcast a message to multiple recipients"""
        logger.info(f"Broadcasting message to {len(recipient_ids)} recipients: {message.message_type}")
        # TODO: Implement actual message broadcasting
        pass
    
    def receive_message(self, sender_id: str, message_type: str = None):
        """Receive messages from a sender"""
        logger.info(f"Receiving messages from {sender_id}")
        # TODO: Implement actual message receiving
        return []
    
    def subscribe(self, recipient_id: str, callback):
        """Subscribe to messages for a recipient"""
        logger.info(f"Subscribing {recipient_id} to messages")
        self.subscribers[recipient_id] = callback
        # TODO: Implement actual subscription logic


if __name__ == '__main__':
    app = create_app()
    
    logger.info("Starting Emergency Response System...")
    logger.info("Control Room API: /cr/incidents")
    logger.info("ERT API: /ert/units/<unit_id>/...")
    logger.info("Health check: /health")
    
    # Run the Flask application
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
