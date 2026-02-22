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
        print(f"[Control Room] 📍 Vehicle Location: {data}")
        ert_id = data.get("ert_id")
        x = data.get("x")
        y = data.get("y")
        # Update unit location in repository if unit service is available
        if self.unit_service:
            try:
                unit = self.unit_service.get_unit_by_id(ert_id)
                if unit:
                    self.unit_service.update_unit(ert_id, x, y)
            except Exception as e:
                print(f"[Control Room] ❌ Failed to update location for {ert_id}: {e}")

    async def handle_acknowledgment(self, data: dict):
        print(f"[Control Room] ✅ Acknowledgment: {data}")

        ert_id = data.get("ert_id")
        incident_id = data.get("incident_id")

        # Create new ert unit if not already exists (unit_service is optional)
        if self.unit_service:
            try:
                unit = self.unit_service.get_unit_by_id(ert_id)
                if not unit:
                    self.unit_service.create_unit(ert_id, data.get("x"), data.get("y"))
            except Exception as e:
                print(f"[Control Room] ❌ Failed to create ERT Unit: {ert_id} ({e})")

        # Add the ert unit to the incident's assigned units list
        incident = self.incident_service.get_incident_by_id(incident_id)
        if incident and ert_id not in incident.assigned_units:
            incident.assigned_units.append(ert_id)
            self.incident_repository.update(incident)

        # Update incident status to acknowledged if it was created before
        if incident and incident.status == IncidentStatus.DISPATCHED:
            incident.status = IncidentStatus.ACKNOWLEDGED
            self.incident_repository.update(incident)

    async def handle_resolution(self, data: dict):
        print(f"[Control Room] 🎉 Resolution: {data}")
        # the data contains ert_id only we can use it to update the incident status to resolved
        # first update the unit status to resolved in the unit repository
    
        ert_id = data.get("ert_id")
        if self.unit_service:
            try:
                unit = self.unit_service.get_unit_by_id(ert_id)
                if unit:
                    self.unit_service.resolve_unit(ert_id)
            except Exception as e:
                print(f"[Control Room] ❌ Failed to update unit status for {ert_id}: {e}")

        # Second iterate over all units assigned to open incident and if all are resolved then update the incident status to resolved as well
        # otherwise keep it "in progress"
        open_incidents = self.incident_service.get_open_incidents()
        for incident in open_incidents:
            if ert_id in incident.assigned_units:
                # Check if all assigned units are resolved
                all_resolved = True
                for assigned_ert_id in incident.assigned_units:
                    assigned_unit = self.unit_service.get_unit_by_id(assigned_ert_id)
                    if assigned_unit and assigned_unit.status != UnitStatus.RESOLVED:
                        all_resolved = False
                        break
                # Update incident status accordingly
                if all_resolved:
                    incident.status = IncidentStatus.RESOLVED
                    self.incident_repository.update(incident)
                    print(f"[Control Room] 🎉 Incident {incident.id} resolved (all units resolved)")
                else:
                    print(f"[Control Room] 🚧 Incident {incident.id} still in progress (some units not resolved)")

    async def handle_disconnection(self, ert_id: str):
        """
        Handle ERT unit disconnection by removing it from assigned units of open incidents
        
        Args:
            ert_id: The ERT unit ID that disconnected
        """
        try:
            open_incidents = self.incident_service.get_open_incidents()
            if not open_incidents:
                print(f"[Control Room] 🚪 ERT Unit {ert_id} disconnected (no open incidents)")
                return
            
            incident = open_incidents[0]
            if ert_id in incident.assigned_units:
                incident.assigned_units.remove(ert_id)
                self.incident_repository.update(incident)
                print(f"[Control Room] 🚪 ERT Unit {ert_id} disconnected and removed from incident {incident.id}")
                print(f"[Control Room] Remaining assigned units: {incident.assigned_units}")
            else:
                print(f"[Control Room] 🚪 ERT Unit {ert_id} disconnected (was not assigned to incident)")
        except Exception as e:
            print(f"[Control Room] ❌ Error handling disconnection for {ert_id}: {e}")