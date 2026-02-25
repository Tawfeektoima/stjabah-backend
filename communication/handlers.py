"""WebSocket message handlers for Control Room subscriptions

Handlers moved out of the service layer to a dedicated module so
the communication layer can subscribe to them directly.
"""
from control_room.model.incident import IncidentStatus
from typing import Any
from control_room.model.unit import UnitStatus

class WebSocketHandlers:
    def __init__(self, incident_service, incident_repository, unit_service=None):
        self.incident_service = incident_service
        self.incident_repository = incident_repository
        self.unit_service = unit_service

    async def handle_location(self, data: dict):
        print(f"[Control Room] \U0001f4cd Vehicle Location: {data}")
        ert_id = data.get("ert_id")
        x = data.get("x")
        y = data.get("y")
        if self.unit_service:
            try:
                unit = self.unit_service.get_unit_by_id(ert_id)
                if unit:
                    self.unit_service.update_unit(ert_id, x, y)
            except Exception as e:
                print(f"[Control Room] \u274c Failed to update location for {ert_id}: {e}")

    async def handle_acknowledgment(self, data: dict):
        print(f"[Control Room] \u2705 Acknowledgment: {data}")
        ert_id = data.get("ert_id")
        incident_id = data.get("incident_id")
        if self.unit_service:
            try:
                unit = self.unit_service.get_unit_by_id(ert_id)
                if not unit:
                    self.unit_service.create_unit(ert_id, data.get("x"), data.get("y"))
            except Exception as e:
                print(f"[Control Room] \u274c Failed to create ERT Unit: {ert_id} ({e})")
        if self.unit_service:
            try:
                self.unit_service.assign_incident_to_unit(ert_id, incident_id)
            except Exception as e:
                print(f"[Control Room] \u274c Failed to assign incident to unit {ert_id}: {e}")
        incident = self.incident_service.get_incident_by_id(incident_id)
        if incident and incident.status == IncidentStatus.DISPATCHED:
            incident.status = IncidentStatus.ACKNOWLEDGED
            self.incident_repository.update(incident)

    async def handle_resolution(self, data: dict):
        print(f"[Control Room] \U0001f389 Resolution: {data}")
        ert_id = data.get("ert_id")
        if self.unit_service:
            try:
                unit = self.unit_service.get_unit_by_id(ert_id)
                if unit:
                    incident_id = unit.assigned_incident
                    self.unit_service.resolve_unit(ert_id)
                    if incident_id:
                        incident = self.incident_service.get_incident_by_id(incident_id)
                        if incident:
                            all_units = self.unit_service.get_all_units()
                            assigned_units = [
                                u for u in all_units
                                if u.assigned_incident == incident_id
                            ]
                            all_resolved = len(assigned_units) > 0 and all(
                                u.status == UnitStatus.RESOLVED
                                for u in assigned_units
                            )
                            if all_resolved:
                                incident.status = IncidentStatus.RESOLVED
                                self.incident_repository.update(incident)
                                print(f"[Control Room] \U0001f389 Incident {incident.id} resolved (all units resolved)")
                            else:
                                print(f"[Control Room] \U0001f6a7 Incident {incident.id} still in progress (some units not resolved)")
            except Exception as e:
                print(f"[Control Room] \u274c Failed to update")

    async def handle_disconnection(self, ert_id: str):
        try:
            if self.unit_service:
                self.unit_service.delete_unit(ert_id)
                print(f"[Control Room] \U0001f6aa ERT Unit {ert_id} disconnected and removed from the system")
            else:
                print(f"[Control Room] \U0001f6aa ERT Unit {ert_id} disconnected (no unit service available)")
        except Exception as e:
            print(f"[Control Room] \u274c Error handling disconnection for {ert_id}: {e}")
