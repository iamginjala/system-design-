import redis
import json
import os
from typing import Optional, Dict, Any

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

def test_connection():
    try:
        return redis_client.ping()
    except redis.ConnectionError:
        return False

