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

## basic cache functions 

def set_data(product_id,my_dict):
    try:
        redis_client.setex(f"product:{product_id}",60,json.dumps(my_dict))
        print(f" data stored successfully under {product_id}")
        return True
    except Exception as e:
        print(f"error storing dictionary {e}")
        return False

def get_data(product_id):
    try:
        raw_data = redis_client.get(f"product:{product_id}")

        if raw_data is None or raw_data == "":
            # print(f"no data found for key {product_id}")
            return f"no data found for key {product_id}"
        if not isinstance(raw_data, (str, bytes, bytearray)):
            return f"invalid data type for key {product_id}"
        data = json.loads(raw_data)
        return data
    except json.JSONDecodeError:
        return f"invalid json data for key {product_id}"
    except Exception as e:
        # print(f"error retrieving dictionary {e}")
        return f"error retrieving dictionary {e}"
    

def delete_data(product_id):
    try:
        deleted = redis_client.delete(f"product:{product_id}")
        if deleted:
            # print("deleted sucessfully")
            return 'deleted successfully'

    except Exception as e:
        # print(f"No data found for this key {product_id}")
        return f"No data found for this key {product_id}"


