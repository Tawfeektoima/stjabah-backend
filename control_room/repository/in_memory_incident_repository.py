from abc import abstractmethod
from typing import Optional, List
from control_room.model.incident import Incident
from control_room.repository.incident_repository import IncidentRepository


class InMemoryIncidentRepository(IncidentRepository):
    """In-memory implementation of Incident repository using dictionary storage"""

    def __init__(self):
        self._storage: dict[str, Incident] = {}

    def create(self, entity: Incident) -> Incident:
        """
        Create a new entity in the database
        
        Args:
            entity: Entity object to create
        
        Returns:
            Created entity with ID
        """
        pass

    def get_by_id(self, entity_id: str) -> Optional[Incident]:
        """
        Retrieve entity by ID from storage
        
        Args:
            entity_id: ID of the entity to retrieve
        
        Returns:
            Entity object if found, None otherwise
        """
        return self._storage.get(entity_id)

    def update(self, entity: Incident) -> Incident:
        """
        Update entity in the database
        
        Args:
            entity: Entity object with updates
        
        Returns:
            Updated entity
        """
        pass
    
    def delete(self, entity_id: str) -> bool:
        """
        Delete entity by ID
        
        Args:
            entity_id: ID of the entity to delete
        
        Returns:
            True if deleted, False otherwise
        """
        pass
    
    def get_all(self) -> Incident:
        """
        Get all entities
        
        Returns:
            List of all entities
        """
        pass