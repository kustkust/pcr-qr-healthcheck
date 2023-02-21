from pydantic import BaseModel
from enum import Enum


class Status(Enum):
    work = "work"
    online = "online"
    offline = "offline"


class InstanceInfo(BaseModel):
    name: str
    status: Status
