import asyncio
import json
import logging
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler

import redis.asyncio as redis
from dotenv import dotenv_values
from pydantic import parse_raw_as

from checker import Checker
from status import InstanceInfo

config = dotenv_values(".env")


def namer(filename):
    log_directory = os.path.split(filename)[0]
    date = os.path.splitext(filename)[1][1:]
    filename = os.path.join(log_directory, date)
    return filename + ".log"


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not os.path.exists("./logs"):
    os.makedirs("./logs")
handler = TimedRotatingFileHandler("./logs/log.log", when="D", interval=int(config["ROTATING_INTERVAL"]), backupCount=5)
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
handler.namer = namer
handler.suffix = "%Y%m%d"
logger.addHandler(handler)

console_handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(console_handler)

check_interval = int(config["CHECK_INTERVAL"])
response_interval = int(config["RESPONSE_INTERVAL"])
camera_channel = config["CAMERA_CHANNEL"]
script_channel = config["SCRIPT_CHANNEL"]
checkers = {
    camera_channel: Checker(instance_type="camera", response_interval=response_interval, logger=logger,
                            names=json.loads(config["CAMERAS"])),
    script_channel: Checker(instance_type="script", response_interval=response_interval, logger=logger,
                            names=json.loads(config["SCRIPTS"])),
}


async def main():
    r = redis.from_url("redis://" + config["HOST"])
    async with r.pubsub() as pubsub:
        await pubsub.subscribe(config["CAMERA_CHANNEL"], config["SCRIPT_CHANNEL"])
        last_check_time = time.time()
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None and message["channel"] is not None:
                checkers[message["channel"].decode()].notify(parse_raw_as(InstanceInfo, message["data"].decode()))
            if time.time() - last_check_time > check_interval:
                last_check_time = time.time()
                for channel in checkers:
                    checkers[channel].check()
            await asyncio.sleep(1)


asyncio.run(main())
