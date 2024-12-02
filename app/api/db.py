import redis


def get_redis_client(connection={'host': 'localhost', 'port': 6379}):
    return redis.Redis(host=connection['host'], port=connection['port'])
