"""In-memory implementation of Incident repository (for testing/development)"""

from typing import Optional, List
from control_room.model.incident import Incident
from control_room.repository.incident_repository import IncidentRepository


class InMemoryIncidentRepository(IncidentRepository):
    """In-memory implementation of Incident repository using dictionary storage"""
    
    def __init__(self):
        self._storage: dict[str, Incident] = {}
    
    def create(self, incident: Incident) -> Incident:
        """Create a new incident in memory"""
        if incident.id is None:
            # Generate ID if not provided
            import uuid
            incident.id = str(uuid.uuid4())
        
        self._storage[incident.id] = incident
        return incident
    
    def get_by_id(self, incident_id: str) -> Optional[Incident]:
        """Retrieve incident by ID from memory"""
        return self._storage.get(incident_id)
    
    def update(self, incident: Incident) -> Incident:
        """Update incident in memory"""
        if incident.id not in self._storage:
            raise ValueError(f"Incident {incident.id} not found")
        self._storage[incident.id] = incident
        return incident
    
    def delete(self, incident_id: str) -> bool:
        """Delete incident by ID from memory"""
        if incident_id in self._storage:
            del self._storage[incident_id]
            return True
        return False
    
    def get_all(self) -> List[Incident]:
        """Get all incidents from memory"""
        return list(self._storage.values())
    
    def get_all_assigned_unit_ids(self, incident_id: str) -> List[str]:
        """Get all unit IDs assigned to an incident"""
        incident = self.get_by_id(incident_id)
        if incident:
            return incident.assigned_unit_ids
        return []
    
    def get_resolved_unit_ids(self, incident_id: str) -> List[str]:
        """Get all unit IDs that have resolved for an incident"""
        # TODO: Implement resolution tracking logic
        # For now, return empty list
        return []
