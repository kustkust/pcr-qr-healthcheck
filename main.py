import asyncio
import time

import redis.asyncio as redis
from pydantic import parse_raw_as

from checker import Checker
from init_logger import init_logger
from settings import settings
from status import InstanceInfo


async def main():
    logger = init_logger()
    checkers = {
        settings.camera_channel: Checker(instance_type="camera", response_interval=settings.response_interval,
                                         logger=logger, names=settings.cameras),
        settings.script_channel: Checker(instance_type="script", response_interval=settings.response_interval,
                                         logger=logger, names=settings.scripts),
    }
    r = redis.from_url("redis://" + settings.redis_host)
    async with r.pubsub() as pubsub:
        await pubsub.subscribe(settings.camera_channel, settings.script_channel)
        last_check_time = time.time()
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None and message["channel"] is not None:
                checkers[message["channel"].decode()].notify(parse_raw_as(InstanceInfo, message["data"].decode()))
            if time.time() - last_check_time > settings.check_interval:
                last_check_time = time.time()
                for channel in checkers:
                    checkers[channel].check()
            await asyncio.sleep(1)


asyncio.run(main())
