import time
from datetime import datetime
from logging import Logger

from status import InstanceInfo, CurrentStatus, Status


class Checker:
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, instance_type: str, response_interval: int, logger: Logger, names: list[str]):
        self.instance_type = instance_type
        self.response_interval = response_interval
        self.logger = logger
        self.current_status = {}
        for name in names:
            self.current_status[name] = CurrentStatus(name=name, last_time=time.time())

    def notify(self, info: InstanceInfo):
        if info.name in self.current_status:
            self.current_status[info.name].last_time = time.time()
            self.current_status[info.name].status = info.status
            self.current_status[info.name].last_datetime = datetime.now()
            self.logger.info(f"{self.instance_type} {info.name}; status {info.status.name}")
        else:
            self.logger.error(f"{self.instance_type} with name {info.name} does not exists")

    def check(self):
        cur_time = time.time()
        for key in self.current_status:
            if cur_time - self.current_status[key].last_time > self.response_interval:
                self.current_status[key].status = Status.not_respond
                self.logger.error(
                    f"{self.instance_type} {key} does not response in the last {cur_time - self.current_status[key].last_time:.2f} seconds")
