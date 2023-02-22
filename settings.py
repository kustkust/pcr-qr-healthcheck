from pydantic import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    project_name: str
    check_interval: int
    response_interval: int
    redis_host: str
    redis_port: int
    camera_channel: str
    script_channel: str
    cameras: list[str]
    scripts: list[str]
    rotating_interval: int
    log_path: str
    local_level_log: str
