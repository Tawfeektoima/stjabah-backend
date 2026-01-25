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

    def __init__(self, id: Optional[str] = None):
        self.id = id
        
    def to_dict(self) -> dict:
        """Convert incident to dictionary for JSON serialization"""
        return {
            'id': self.id
        }
