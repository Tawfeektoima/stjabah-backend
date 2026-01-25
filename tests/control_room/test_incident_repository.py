"""Unit tests for Incident Repository"""

import unittest
from control_room.repository.in_memory_incident_repository import InMemoryIncidentRepository
from control_room.model.incident import Incident, IncidentStatus


class TestIncidentRepository(unittest.TestCase):
    """Test cases for incident repository get_by_id method"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repository = InMemoryIncidentRepository()
    
    def test_get_by_id_returns_incident_when_exists(self):
        """Test get_by_id returns incident when it exists in storage"""
        # Arrange
        incident = Incident(
            id="INC-001"
        )
        self.repository._storage["INC-001"] = incident
        
        # Act
        result = self.repository.get_by_id("INC-001")
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "INC-001")
    
    def test_get_by_id_returns_none_when_not_found(self):
        """Test get_by_id returns None when incident doesn't exist"""
        # Act
        result = self.repository.get_by_id("NON-EXISTENT")
        
        # Assert
        self.assertIsNone(result)
    
    def test_get_by_id_returns_none_for_empty_storage(self):
        """Test get_by_id returns None when storage is empty"""
        # Act
        result = self.repository.get_by_id("INC-001")
        
        # Assert
        self.assertIsNone(result)
    
    def test_get_by_id_returns_correct_incident_with_multiple_incidents(self):
        """Test get_by_id returns correct incident when multiple exist"""
        # Arrange
        incident1 = Incident(id="INC-001")
        incident2 = Incident(id="INC-002")
        incident3 = Incident(id="INC-003")
        
        self.repository._storage["INC-001"] = incident1
        self.repository._storage["INC-002"] = incident2
        self.repository._storage["INC-003"] = incident3
        
        # Act
        result = self.repository.get_by_id("INC-002")
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "INC-002")


if __name__ == '__main__':
    unittest.main()