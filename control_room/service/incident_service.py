"""Business logic for Control Room incident management"""

import uuid
from typing import List
from control_room.repository.in_memory_incident_repository import InMemoryIncidentRepository
from control_room.model.incident import Incident, IncidentStatus
from communication.websocket_communication import WebSocketCommunication


class IncidentService:
    def __init__(
        self,
        incident_repository: InMemoryIncidentRepository,
        communication_channel: WebSocketCommunication
    ):
        self.incident_repository = incident_repository
        self.communication_channel = communication_channel

    def create_incident(self, x: float, y: float) -> Incident:
        incident = Incident(
            x=x,
            y=y,
            status=IncidentStatus.CREATED
        )
        created_incident = self.incident_repository.create(incident)
        return created_incident

    def get_incident_by_id(self, incident_id: str):
        return self.incident_repository.get_by_id(incident_id)

    def update_incident(self, incident_id: str, x: float, y: float):
        incident = self.incident_repository.get_by_id(incident_id)
        if not incident:
            raise ValueError(f"Incident with ID {incident_id} does not exist.")
        incident.x = x
        incident.y = y
        updated_incident = self.incident_repository.update(incident)
        return updated_incident

    def get_all_incidents(self) -> List[Incident]:
        return self.incident_repository.get_all()

    def delete_incident(self, incident_id: str) -> bool:
        return self.incident_repository.delete(incident_id)

    def get_open_incidents(self) -> List[Incident]:
        all_incidents = self.incident_repository.get_all()
        open_incidents = [
            incident for incident in all_incidents
            if incident.status != IncidentStatus.RESOLVED
        ]
        return open_incidents

    async def dispatch_incident(self, incident_id: str):
        incident = self.incident_repository.get_by_id(incident_id)
        if incident is None:
            raise ValueError(f"Incident with ID {incident_id} does not exist.")
        incident.status = IncidentStatus.DISPATCHED
        self.incident_repository.update(incident)
        await self.communication_channel.publish(

             topic="incident",
            message=incident.to_dict()
        )

        return True
