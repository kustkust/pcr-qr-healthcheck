from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Status(Enum):
    not_init = "not_init"
    not_respond = "not_respond"
    work = "work"
    online = "online"
    offline = "offline"


class InstanceInfo(BaseModel):
    name: str
    status: Status


class CurrentStatus(BaseModel):
    name: str
    status: Status = Status.not_init
    last_time: float
    last_datetime: datetime | None = None
