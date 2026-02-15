"""Business logic for Control Room incident management"""

import uuid
from control_room.repository.in_memory_incident_repository import InMemoryIncidentRepository
from control_room.model.incident import Incident, IncidentStatus
from communication.websocket_communication import WebSocketCommunication
from typing import List

class IncidentService:
    """Service layer for incident operations"""
    
    def __init__(self, incident_repository: InMemoryIncidentRepository, communication_channel: WebSocketCommunication):
        self.incident_repository = incident_repository
        self.communication_channel = communication_channel
    
    def create_incident(self, x, y: float) -> Incident:
        """
        Create a new incident in the system
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Created incident object
        """
        incident = Incident(
            x=x,
            y=y,
            status=IncidentStatus.CREATED
        )
        created_incident = self.incident_repository.create(incident)

        # Notify ERT units about the new incident
        # self.communication_channel.notify_units_new_incident(created_incident)
        
        return created_incident
    
    def get_incident_by_id(self, incident_id: str):
        """
        Retrieve incident by ID from repository
        
        Args:
            incident_id: ID of the incident to retrieve
        
        Returns:
            Incident object if found, None otherwise
        """
        return self.incident_repository.get_by_id(incident_id)
    
    def dispatch_incident(self, incident_id: str, unit_ids: list):
        """
        Dispatch incident to specific ERT vehicles
        
        Args:
            incident_id: ID of the incident
            unit_ids: List of ERT unit IDs to dispatch to
        
        Returns:
            Dispatch result
        """
        pass
    
    def check_and_resolve_incident(self, incident_id: str):
        """
        Check if all assigned units have resolved.
        If the last unit resolves, mark incident as Resolved
        
        Args:
            incident_id: ID of the incident to check
        """
        pass

    def update_incident(self, incident_id: str, x: float, y: float):
        """
        Update incident coordinates

        Args:
            incident_id: ID of the incident
            x: New x coordinate
            y: New y coordinate
        """
        incident = self.incident_repository.get_by_id(incident_id)
        if not incident:
            raise ValueError(f"Incident with ID {incident_id} does not exist.")
        
        incident.x = x
        incident.y = y
        updated_incident = self.incident_repository.update(incident)
        return updated_incident
        
    def get_all_incidents(self) -> List[Incident]:
        """
        Get all incidents with optional status filtering
        """
        return self.incident_repository.get_all()
    
    def delete_incident(self, incident_id: str) -> bool:
        """
        Delete an incident from the system
        
        Args:
            incident_id: The unique identifier of the incident to delete
            
        Returns:
            True if incident was deleted successfully, False if incident was not found
        """
        return self.incident_repository.delete(incident_id)
    
    def get_open_incidents(self) -> List[Incident]:
        """
        Get all open incidents (not resolved)
        
        Returns:
            List of open incidents
        """
        all_incidents = self.incident_repository.get_all()
        open_incidents = [incident for incident in all_incidents if incident.status != IncidentStatus.RESOLVED]
        return open_incidents
    
    async def dispatch_incident(self, incident_id: str):
        """
        Dispatch incident to all vehicles
        
        Args:
            incident_id: ID of the incident        
        Returns:
            Dispatch result
        """
        incident = self.incident_repository.get_by_id(incident_id)

        if incident is None:
            raise ValueError(f"Incident with ID {incident_id} does not exist.")
        
        # Notify ERT units about the incident and wait for acknowledgment
        await self.communication_channel.publish(
            topic="new_incident",
            message=incident.to_dict()
        )

        return True

    async def handle_location(self, data:dict):
        print(f"[Control Room] 📍 Vehicle Location: {data}")

    async def handle_acknowledgment(self, data:dict):
        print(f"[Control Room] ✅ Acknowledgment: {data}")

    async def handle_resolution(self, data:dict):
        print(f"[Control Room] 🎉 Resolution: {data}")