import asyncio
import json
import websockets
from collections import defaultdict

# Store subscriptions: topic -> set of connected sockets
subscriptions = defaultdict(set)
connected_clients = set()

async def handler(websocket):
    print(f"Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")
            topic = data.get("topic")

            # 1. Handle Subscription Requests
            if msg_type == "subscribe":
                subscriptions[topic].add(websocket)
                print(f"Client subscribed to '{topic}'")

            # 2. Handle Publish Requests
            elif msg_type == "publish":
                payload = data.get("payload")
                print(f"Broadcasting message on '{topic}': {payload}")
                
                # Forward the message to everyone subscribed to this topic
                # EXCLUDING the sender (optional, usually desired)
                if topic in subscriptions:
                    # Create the standard message format
                    response = json.dumps({
                        "topic": topic,
                        "payload": payload
                    })
                    
                    # Send to all subscribers
                    subscribers = subscriptions[topic]
                    for subscriber in subscribers:
                        # Optional: Don't echo back to sender if you don't want to
                        # if subscriber != websocket: 
                        await subscriber.send(response)

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        # Cleanup
        connected_clients.remove(websocket)
        for topic in subscriptions:
            subscriptions[topic].discard(websocket)

async def main():
    # Listen on all interfaces (0.0.0.0) on port 8765
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Hub Server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())