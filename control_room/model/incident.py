"""Data models for incidents"""

from enum import Enum
from datetime import datetime
from typing import Optional

class IncidentStatus(Enum):
    """Incident status enumeration"""
    CREATED = "created"
    DISPATCHED = "dispatched"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    PENDING = "pending"


class Incident:
    """Incident model"""

    def __init__(
        self, 
        x: float,
        y: float,
        status: IncidentStatus = IncidentStatus.CREATED,
        created_at: Optional[datetime] = None,
        resolved_at: Optional[datetime] = None,
        id: Optional[str] = None,
        assigned_units: Optional[list] = None
    ):
        self.id = id
        self.x = x
        self.y = y
        self.status = status
        self.created_at = created_at
        self.resolved_at = resolved_at
        self.assigned_units = assigned_units or []

    def to_dict(self) -> dict:
        """Convert incident to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'assigned_units': self.assigned_units
        }
