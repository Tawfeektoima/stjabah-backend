"""
Control Room Application Entry Point
Integrated Flask API + WebSocket Communication
"""
import asyncio
import sys
import logging
import threading
from pathlib import Path
from flask import Flask

# Add parent directory to Python path to resolve imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from control_room.repository.in_memory_incident_repository import InMemoryIncidentRepository
from control_room.service.incident_service import IncidentService
from control_room.api.incident_api import control_room_bp, init_control_room_api
from communication.websocket_communication import WebSocketCommunication

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ControlRoomApplication:
    """Control Room application with Flask API and WebSocket communication"""
    
    def __init__(self):
        # Initialize repositories
        self.incident_repository = InMemoryIncidentRepository()
        
        # Initialize communication channel
        self.communication_channel = WebSocketCommunication()
        
        # Initialize service with callbacks from Service Layer
        self.incident_service = IncidentService(
            incident_repository=self.incident_repository,
            communication_channel=self.communication_channel
        )
        
        # Create Flask app
        self.app = self._create_flask_app()
    
    def _create_flask_app(self):
        """Create and configure the Flask application"""
        app = Flask(__name__)
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
        
        logger.info("📋 Registering Control Room blueprints...")
        control_room_bp_instance = init_control_room_api(self.incident_service)
        app.register_blueprint(control_room_bp_instance, url_prefix='/cr')
        
        # Health check endpoint
        @app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return {
                'status': 'healthy',
                'service': 'emergency-response-system',
                'component': 'control-room'
            }, 200
        
        logger.info("✓ Flask application configured successfully")
        return app
    
    async def setup_websocket(self):
        """
        Setup: Initialize WebSocket connection and subscriptions
        Following Golden Rule: Subscriptions happen during startup, not in requests
        """
        try:
            logger.info("🔌 Connecting to Hub WebSocket server...")
            await self.communication_channel.connect("ws://localhost:8765")
            
            logger.info("📡 Setting up WebSocket subscriptions...")
            # Subscribe to ERT messages using callbacks from Service Layer
            await self.communication_channel.subscribe(
                "location", 
                self.incident_service.handle_location
            )
            await self.communication_channel.subscribe(
                "acknowledgment", 
                self.incident_service.handle_acknowledgment
            )
            await self.communication_channel.subscribe(
                "resolution", 
                self.incident_service.handle_resolution
            )
            
            logger.info("✓ Control Room ready for incident dispatching")
            
        except Exception as e:
            logger.error(f"Failed to setup Control Room: {e}")
            raise
    
    async def run_websocket_loop(self):
        """Run the WebSocket connection loop"""
        try:
            await self.setup_websocket()
            
            # Keep the WebSocket connection alive
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down WebSocket loop...")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self.communication_channel.disconnect()
            logger.info("Control Room offline")
    
    def run_flask(self):
        """Run the Flask application"""
        logger.info("🚀 Starting Flask API server...")
        logger.info("   Control Room API: http://127.0.0.1:5001/cr/incidents")
        logger.info("   Health check: http://127.0.0.1:5001/health")
        
        self.app.run(
            host='127.0.0.1',
            port=5001,
            debug=False,  # Set to False to avoid double startup messages
            use_reloader=False  # Disable reloader in threaded mode
        )
    
    def start(self):
        """Start both Flask and WebSocket in separate threads"""
        # Start Flask in a separate thread
        flask_thread = threading.Thread(target=self.run_flask, daemon=False)
        flask_thread.start()
        
        # Run WebSocket event loop in the main thread
        # Create a new event loop instead of calling asyncio.run() from within an existing loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_websocket_loop())
        finally:
            loop.close()


def main():
    """Entry point"""
    logger.info("=" * 60)
    logger.info("🎛️  Control Room Application Starting")
    logger.info("=" * 60)
    
    control_room = ControlRoomApplication()
    control_room.start()


if __name__ == "__main__":
    main()