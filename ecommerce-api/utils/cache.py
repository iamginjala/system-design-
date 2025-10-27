import redis
import json
import os
from typing import Optional, Dict, Any
from .logger import get_app_logger,get_request_logger,get_error_logger

app_logger = get_app_logger()
request_logger = get_request_logger()
error_logger = get_error_logger()




# Try REDIS_URL first (for Render), fall back to REDIS_HOST/PORT (for local)
redis_url = os.getenv('REDIS_URL')
if redis_url:
    redis_client = redis.from_url(redis_url, decode_responses=True)
else:
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

## basic cache functions 

def set_data(product_id,my_dict):
    try:
        redis_client.setex(f"product:{product_id}",60,json.dumps(my_dict))
        app_logger.debug(f"data stored successfully under {product_id}")
        return True
    except Exception as e:
        error_logger.error(f"Error message: {e}",exc_info=True)
        return False

def get_data(product_id):
    try:
        raw_data = redis_client.get(f"product:{product_id}")

        if raw_data is None or raw_data == "":
            request_logger.info(f"no data found for key {product_id}")
            return f"no data found for key {product_id}"
        if not isinstance(raw_data, (str, bytes, bytearray)):
            error_logger.error(f"invalid data type for key {product_id}")
            return f"invalid data type for key {product_id}"
        data = json.loads(raw_data)
        return data
    except json.JSONDecodeError:
        error_logger.error(f"invalid json data for key {product_id}")
        return f"invalid json data for key {product_id}"
    except Exception as e:
        error_logger.error(f"Error message: {e}",exc_info=True)
        return f"error retrieving dictionary {e}"
    

def delete_data(product_id):
    try:
        deleted = redis_client.delete(f"product:{product_id}")
        if deleted:
            request_logger.info("cache deleted successfully")
            return 'deleted successfully'
        else:
            request_logger.info(f"no data found for {product_id}")
            return f"no data found for {product_id}"

    except Exception as e:
        error_logger.error(f"No data found for this key {product_id}",exc_info=True)
        return f"No data found for this key {product_id}"


