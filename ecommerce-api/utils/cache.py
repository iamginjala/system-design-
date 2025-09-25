import redis

redis_cli = redis.Redis(host='redis',port=6379,decode_responses=True)

connection = redis_cli.ping()

print(connection)