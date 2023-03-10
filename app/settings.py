import os.path

from pydantic import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = "../config/.env" if (os.path.exists("../config/.env")) else "./config/.env"

    project_name: str
    check_interval: int
    response_interval: int
    redis_host: str
    redis_port: int
    fastapi_host: str
    fastapi_port: int
    camera_channel: str
    script_channel: str
    owen_channel: str
    cameras: list[str]
    scripts: list[str]
    owens: list[str]
    log_backup_count: int
    log_path: str
    local_level_log: str
