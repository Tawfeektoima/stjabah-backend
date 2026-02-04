"""Abstract communication channel for Control Room and ERT communication"""

from abc import ABC, abstractmethod
from typing import Callable, Any

# Abstract base class
class Communication(ABC):
    @abstractmethod
    async def connect(self, url: str, **kwargs) -> bool:
        """Connect to the communication service"""
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str, callback: Callable) -> bool:
        """Subscribe to a topic/channel"""
        pass
    
    @abstractmethod
    async def publish(self, topic: str, message: Any) -> bool:
        """Publish a message to a topic/channel"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the communication service"""
        pass
