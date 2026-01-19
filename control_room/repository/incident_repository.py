"""Incident repository interface for common repository operations"""

from abc import ABC, abstractmethod
from typing import TypeVar, Optional, List

T = TypeVar('T')


class IncidentRepository(ABC):
    """Abstract base repository interface defining common CRUD operations"""
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """
        Create a new entity in the database
        
        Args:
            entity: Entity object to create
        
        Returns:
            Created entity with ID
        """
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Retrieve entity by ID
        
        Args:
            entity_id: ID of the entity
        
        Returns:
            Entity object or None if not found
        """
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """
        Update entity in the database
        
        Args:
            entity: Entity object with updates
        
        Returns:
            Updated entity
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """
        Delete entity by ID
        
        Args:
            entity_id: ID of the entity to delete
        
        Returns:
            True if deleted, False otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Get all entities
        
        Returns:
            List of all entities
        """
        pass
