import time
from logging import Logger
from typing import Any

from pydantic import BaseModel

from status import InstanceInfo


class Checker(BaseModel):
    instance_type: str
    response_interval: int
    logger: Logger
    last_respond_time: dict[str, float] = {}

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, names, **data: Any):
        super().__init__(**data)
        for name in names:
            self.last_respond_time[name] = time.time()

    def notify(self, status: InstanceInfo):
        if status.name in self.last_respond_time:
            self.last_respond_time[status.name] = time.time()
            self.logger.info(f"{self.instance_type} {status.name}; status {status.status.name}")
        else:
            self.logger.error(f"{self.instance_type} with name {status.name} does not exists")

    def check(self):
        cur_time = time.time()
        for key in self.last_respond_time:
            if cur_time - self.last_respond_time[key] > self.response_interval:
                self.logger.error(
                    f"{self.instance_type} {key} does not response in the last {cur_time - self.last_respond_time[key]:.2f} seconds")
