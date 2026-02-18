import asyncio
import sys
from pathlib import Path

from flask import json

# Add parent directory to Python path to resolve imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from communication.websocket_communication import WebSocketCommunication

# get id from unit_info.json file
with open("ert/unit_info.json", "r") as f:
    unit_info = json.load(f)
    ert_id = unit_info["id"]

# --- Callbacks ---
async def on_new_incident(data):
    """Handle incoming incident from control room"""
    print(f"\n[ERT-{ert_id}] 🚨 RECEIVED INCIDENT: {data}")
    print(f"[ERT-{ert_id}] Preparing vehicle...")
    
    incident_id = data.get("id")
    unit_info["assigned_incident"] = data  # Store the full incident data
    
    # Update unit_info.json with assigned incident and status
    unit_info["status"] = "dispatched"
    with open("ert/unit_info.json", "w") as f:
        json.dump(unit_info, f, indent=4)
    print(f"[ERT-{ert_id}] Updated unit info with assigned incident: {incident_id}")
    
    # Send acknowledgment to control room
    acknowledgment = {
        "ert_id": ert_id,
        "incident_id": incident_id,
        "x": data.get("x", 100),
        "y": data.get("y", 200),
        "message": "Incident received successfully. ERT unit dispatched.",
        "status": "acknowledged"
    }
    
    await ert_comms.publish("acknowledgment", acknowledgment)
    print(f"[ERT-{ert_id}] ✅ Acknowledgment sent to control room")

# --- Main ERT Logic ---
ert_comms = WebSocketCommunication()

async def main():
    # 1. Connect to Hub and register in one call
    await ert_comms.connect(
        "ws://localhost:8765",
        client_type="ert",
        client_id=ert_id
    )
    print(f"[ERT-{ert_id}] Connected and registered with hub")
    
    # 2. Subscribe to Incidents
    await ert_comms.subscribe("new_incident", on_new_incident)
    print(f"[ERT-{ert_id}] Subscribed to incident notifications")
    
    # 3. Simulation Loop (sending location updates)
    while True:
        # Simulate GPS coordinates
        location_data = {
            "ert_id": ert_id,
            "lat": 30.0444, 
            "lng": 31.2357, 
            "speed": 60
        }
        
        print(f"[ERT-{ert_id}] Sending Location...")
        await ert_comms.publish("location", location_data)
        
        await asyncio.sleep(5)  # Send every 5 seconds

if __name__ == "__main__":
    asyncio.run(main())