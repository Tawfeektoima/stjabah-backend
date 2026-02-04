import asyncio
import sys
from pathlib import Path

# Add parent directory to Python path to resolve imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from communication.websocket_communication import WebSocketCommunication

# --- Callbacks ---
async def on_location(data):
    print(f"[Control Room] 📍 Vehicle Location: {data}")

async def on_ack(data):
    print(f"[Control Room] ✅ Acknowledgment: {data}")

async def on_resolution(data):
    print(f"[Control Room] 🎉 Resolution: {data}")

# --- Main Control Room Logic ---
cr_comms = WebSocketCommunication()

async def main():
    # 1. Connect to Hub (localhost since it's on the same server)
    await cr_comms.connect("ws://localhost:8765")

    # 2. Subscribe to Vehicle Updates
    await cr_comms.subscribe("location", on_location)
    await cr_comms.subscribe("Acknowledgment", on_ack)
    await cr_comms.subscribe("resolution", on_resolution)

    # 3. Simulate creating an incident after a few seconds
    await asyncio.sleep(2)
    incident_data = {
        "id": 101,
        "type": "Fire",
        "address": "123 Main St",
        "severity": "High"
    }
    print(f"\n[Control Room] 📤 Dispatching Incident #{incident_data['id']}...")
    await cr_comms.publish("new_incident", incident_data)
    
    # Keep script running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())