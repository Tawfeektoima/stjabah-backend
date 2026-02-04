import json
import asyncio
import websockets
from typing import Callable, Any, Dict, List
from communication.communication import Communication

class WebSocketCommunication(Communication):
    def __init__(self):
        self.connection = None
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.is_connected = False

    async def connect(self, url: str, **kwargs) -> bool:
        try:
            self.connection = await websockets.connect(url, **kwargs)
            self.is_connected = True
            # Start listening in the background
            asyncio.create_task(self._listen())
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        if self.connection:
            await self.connection.close()
            self.is_connected = False
            return True
        return False

    async def subscribe(self, topic: str, callback: Callable) -> bool:
        # 1. Register callback locally
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(callback)
        
        # 2. Tell the Hub we want this topic
        msg = {"type": "subscribe", "topic": topic}
        await self.connection.send(json.dumps(msg))
        return True

    async def publish(self, topic: str, message: Any) -> bool:
        if not self.is_connected: return False
        
        # Wrap in the format the Hub expects
        msg = {
            "type": "publish",
            "topic": topic,
            "payload": message
        }
        await self.connection.send(json.dumps(msg))
        return True

    async def _listen(self):
        try:
            async for raw_msg in self.connection:
                data = json.loads(raw_msg)
                topic = data.get("topic")
                payload = data.get("payload")
                
                # Trigger callbacks
                if topic in self.subscriptions:
                    for cb in self.subscriptions[topic]:
                        if asyncio.iscoroutinefunction(cb):
                            await cb(payload)
                        else:
                            cb(payload)
        except Exception as e:
            print(f"Listen loop error: {e}")
            self.is_connected = False