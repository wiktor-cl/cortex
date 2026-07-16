from redis import Redis
from rq import Queue

from worker.config import get_settings


def get_redis_connection() -> Redis:
    return Redis.from_url(get_settings().redis_url)


def get_queue() -> Queue:
    return Queue(get_settings().queue_name, connection=get_redis_connection())
