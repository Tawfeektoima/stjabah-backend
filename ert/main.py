import asyncio
import sys
from pathlib import Path

# Add parent directory to Python path to resolve imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from communication.WebSocketCommunication import WebSocketCommunication

# --- Callbacks ---
async def on_new_incident(data):
    print(f"\n[ERT] 🚨 RECEIVED INCIDENT: {data}")
    print("[ERT] Preparing vehicle...")
    
    # Immediately Acknowledge
    await ert_comms.publish("Acknowledgment", {"status": "Received", "id": data['id']})

# --- Main ERT Logic ---
ert_comms = WebSocketCommunication()

async def main():
    # 1. Connect to Hub (Replace localhost with Control Room Domain/IP)
    await ert_comms.connect("ws://localhost:8765")
    
    # 2. Subscribe to Incidents
    await ert_comms.subscribe("new incident", on_new_incident)
    
    # 3. Simulation Loop (sending location updates)
    while True:
        # Simulate GPS coordinates
        location_data = {"lat": 30.0444, "lng": 31.2357, "speed": 60}
        
        print("[ERT] Sending Location...")
        await ert_comms.publish("location", location_data)
        
        await asyncio.sleep(5) # Send every 5 seconds

if __name__ == "__main__":
    asyncio.run(main())