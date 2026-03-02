"""Data models for units"""

from enum import Enum
from datetime import datetime
from typing import Optional

class UnitStatus(Enum):
    """Unit status enumeration"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    UNAVAILABLE = "unavailable"

class Unit:
    """Unit model"""

    def __init__(
        self, 
        id: str,
        x: float,
        y: float,
        status: 'UnitStatus' = None,
        assigned_incident: Optional[str] = None
    ):
        self.id = id
        self.x = x
        self.y = y
        self.status = status or UnitStatus.ACTIVE
        self.assigned_incident = assigned_incident

    def to_dict(self) -> dict:
        """Convert unit to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'status': self.status.value,
            'assigned_incident': self.assigned_incident
        }
