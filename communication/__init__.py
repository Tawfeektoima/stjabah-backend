"""Communication module for abstracting communication between Control Room and ERT"""

from communication.communication import Communication
from communication.websocket_communication import WebSocketCommunication

__all__ = ['Communication', 'WebSocketCommunication']
