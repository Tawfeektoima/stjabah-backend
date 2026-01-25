"""Unit tests for Incident API"""

import unittest
from unittest.mock import Mock
from flask import Flask
from control_room.api.incident_api import init_control_room_api
from control_room.model.incident import Incident


class TestIncidentAPI(unittest.TestCase):
    """Test cases for GET /control_room/incidents/<id> endpoint"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.incident_service = Mock()
        
        # Set up Flask app
        self.app = Flask(__name__)
        control_room_bp = init_control_room_api(self.incident_service)
        self.app.register_blueprint(control_room_bp)
        self.client = self.app.test_client()
    
    def test_get_incident_returns_200_when_incident_found(self):
        """Test GET /cr/incidents/<id> returns 200 when incident exists"""
        # Arrange
        incident = Incident(id="INC-001")
        self.incident_service.get_incident_by_id.return_value = incident
        
        # Act
        response = self.client.get('/incidents/INC-001')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json)
        self.incident_service.get_incident_by_id.assert_called_once_with("INC-001")
    
    def test_get_incident_returns_404_when_incident_not_found(self):
        """Test GET /cr/incidents/<id> returns 404 when incident doesn't exist"""
        # Arrange
        self.incident_service.get_incident_by_id.return_value = None
        
        # Act
        response = self.client.get('/incidents/NON-EXISTENT')
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'Incident not found')
        self.assertEqual(response.json['incident_id'], 'NON-EXISTENT')
        self.incident_service.get_incident_by_id.assert_called_once_with("NON-EXISTENT")
    
    def test_get_incident_returns_404_with_correct_error_structure(self):
        """Test 404 response contains proper error structure"""
        # Arrange
        self.incident_service.get_incident_by_id.return_value = None
        
        # Act
        response = self.client.get('/incidents/INC-999')
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Incident not found')
        self.assertEqual(response.json['incident_id'], 'INC-999')
        self.assertEqual(len(response.json), 2)  # Only error and incident_id fields
    
    def test_get_incident_handles_service_exception(self):
        """Test GET /cr/incidents/<id> handles service layer exceptions"""
        # Arrange
        self.incident_service.get_incident_by_id.side_effect = Exception("Database error")
        
        # Act
        response = self.client.get('/incidents/INC-001')
        
        # Assert
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'Internal server error')
    
    def test_get_incident_handles_different_incident_ids(self):
        """Test endpoint handles different incident ID formats"""
        # Arrange
        incident_ids = ["INC-001", "INC-999", "INCIDENT-ABC-123", "12345"]
        
        for incident_id in incident_ids:
            incident = Incident(id=incident_id)
            self.incident_service.get_incident_by_id.return_value = incident
            
            # Act
            response = self.client.get(f'/incidents/{incident_id}')
            
            # Assert
            self.assertEqual(response.status_code, 200)
            self.incident_service.get_incident_by_id.assert_called_with(incident_id)


if __name__ == '__main__':
    unittest.main()