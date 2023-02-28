import asyncio
import time

import redis.asyncio as redis
from pydantic import parse_raw_as

from checker import Checker
from init_logger import init_logger
from settings import Settings
from status import InstanceInfo


async def main():
    settings = Settings()
    logger = init_logger(settings)
    checkers = {
        settings.camera_channel: Checker(instance_type="camera", response_interval=settings.response_interval,
                                         logger=logger, names=settings.cameras),
        settings.script_channel: Checker(instance_type="script", response_interval=settings.response_interval,
                                         logger=logger, names=settings.scripts),
        settings.owen_channel: Checker(instance_type="owen", response_interval=settings.response_interval,
                                       logger=logger, names=settings.owens)
    }
    redis_host = "redis://" + settings.redis_host + ":" + str(settings.redis_port)
    r = redis.from_url(redis_host)
    async with r.pubsub() as pubsub:
        try:
            logger.info(f"Connecting to redis {redis_host}")
            await pubsub.subscribe(*list(checkers.keys()))
        except:
            logger.error(f"Fail to connect to redis {redis_host}")
            return
        logger.info(f"Connect to redis {redis_host}")
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
