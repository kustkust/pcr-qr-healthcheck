import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from settings import settings


def init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def namer(filename):
        log_directory = os.path.split(filename)[0]
        date = os.path.splitext(filename)[1][1:]
        filename = os.path.join(log_directory, date)
        return filename + ".log"

    if not os.path.exists(settings.log_path):
        os.makedirs(settings.log_path)
    handler = TimedRotatingFileHandler(settings.log_path + "log.log", when="D", interval=settings.rotating_interval)
    handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
    handler.namer = namer
    handler.suffix = "%Y%m%d"
    logger.addHandler(handler)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(console_handler)

    return logger
