import time

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi_utils.tasks import repeat_every
from pydantic import parse_raw_as

import schemas
from checker import Checker
from init_logger import init_logger
from settings import Settings
from status import InstanceInfo

settings = Settings()
logger = init_logger(settings)
checkers: dict[str, Checker] = {
    settings.camera_channel: Checker(instance_type="camera", response_interval=settings.response_interval,
                                     logger=logger, names=settings.cameras),
    settings.script_channel: Checker(instance_type="script", response_interval=settings.response_interval,
                                     logger=logger, names=settings.scripts),
    settings.owen_channel: Checker(instance_type="owen", response_interval=settings.response_interval,
                                   logger=logger, names=settings.owens)
}
app = FastAPI()
pubsub: redis.client.PubSub | None = None
last_check_time = time.time()


@app.on_event("startup")
async def init_redis():
    global pubsub
    redis_host = "redis://" + settings.redis_host + ":" + str(settings.redis_port)
    r = redis.from_url(redis_host)
    pubsub = r.pubsub()
    try:
        logger.info(f"Connecting to redis {redis_host}")
        await pubsub.subscribe(*list(checkers.keys()))
        logger.info(f"Connect to redis {redis_host}")
    except:
        logger.error(f"Fail to connect to redis {redis_host}")
        raise Exception()


@app.on_event("startup")
@repeat_every(seconds=1)
async def redis_cycle():
    global last_check_time, pubsub
    if pubsub is None:
        return
    while (message := await pubsub.get_message(ignore_subscribe_messages=True)) is not None:
        if message["channel"] is not None:
            checkers[message["channel"].decode()].notify(parse_raw_as(InstanceInfo, message["data"].decode()))
    if time.time() - last_check_time > settings.check_interval:
        last_check_time = time.time()
        for channel in checkers:
            checkers[channel].check()


def to_info(item) -> schemas.Info:
    return schemas.Info(name=item.name, status=str(item.status), last_notification_time=item.last_datetime)


@app.get("/get_status", response_model=dict[str, list[schemas.Info]])
async def get_status():
    res = {}
    for key in checkers:
        res[key] = [to_info(item) for item in checkers[key].current_status.values()]
    return res


@app.get("/get_channel_status", response_model=list[schemas.Info])
async def get_channel_status(channel: str):
    if channel not in checkers.keys():
        raise HTTPException(status_code=404, detail=f"channel {channel} not found")
    return [to_info(item) for item in checkers[channel].current_status.values()]


@app.get("/get_item_status", response_model=schemas.Info)
async def get_item_status(channel: str, name: str):
    if channel not in checkers.keys():
        raise HTTPException(status_code=404, detail=f"channel {channel} not found")
    elif name not in checkers[channel].current_status.keys():
        raise HTTPException(status_code=404, detail=f"{checkers[channel].instance_type} with name {name} not found")
    return to_info(checkers[channel].current_status[name])


uvicorn.run(app, host=settings.fastapi_host, port=settings.fastapi_port)
