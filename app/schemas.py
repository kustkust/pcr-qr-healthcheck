import datetime

from pydantic import BaseModel


class Info(BaseModel):
    name: str
    status: str
    last_notification_time: datetime.datetime | None
