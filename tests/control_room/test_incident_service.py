"""Unit tests for Incident Service"""

import unittest
from unittest.mock import Mock
from control_room.repository.in_memory_incident_repository import InMemoryIncidentRepository
from control_room.service.incident_service import IncidentService
from control_room.model.incident import Incident


class TestIncidentService(unittest.TestCase):
    """Test cases for incident service get_incident_by_id"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.incident_repository = InMemoryIncidentRepository()
        self.communication_channel = Mock()
        self.incident_service = IncidentService(
            self.incident_repository,
            self.communication_channel
        )
    
    def test_get_incident_by_id_returns_incident_when_exists(self):
        """Test get_incident_by_id returns incident when it exists"""
        # Arrange
        incident = Incident(id="INC-001")
        self.incident_repository._storage["INC-001"] = incident
        
        # Act
        result = self.incident_service.get_incident_by_id("INC-001")
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "INC-001")
    
    def test_get_incident_by_id_returns_none_when_not_found(self):
        """Test get_incident_by_id returns None when incident doesn't exist"""
        # Act
        result = self.incident_service.get_incident_by_id("NON-EXISTENT")
        
        # Assert
        self.assertIsNone(result)
    
    def test_get_incident_by_id_calls_repository_with_correct_id(self):
        """Test get_incident_by_id calls repository with correct incident_id"""
        # Arrange
        incident = Incident(id="INC-002")
        self.incident_repository._storage["INC-002"] = incident
        
        # Act
        result = self.incident_service.get_incident_by_id("INC-002")
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "INC-002")


if __name__ == '__main__':
    unittest.main()