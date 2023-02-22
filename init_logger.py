import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from settings import Settings


def init_logger(logger_setting: Settings):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not os.path.exists(logger_setting.log_path):
        os.makedirs(logger_setting.log_path)
    rotate_handler = logging.handlers.TimedRotatingFileHandler(
        logger_setting.log_path + logger_setting.project_name + ".log",
        when='midnight',
        interval=1,
        backupCount=logger_setting.rotating_interval
    )
    rotate_handler.setLevel(logger_setting.local_level_log)
    rotate_handler.setFormatter(
        logging.Formatter(
            f'%(asctime)s.%(msecs)3d [%(levelname)12s] [%(pathname)s %(funcName)s %(lineno)d] %(message)s',
            '%z %Y-%m-%d %H:%M:%S',
        )
    )
    logger.addHandler(rotate_handler)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(console_handler)

    return logger
