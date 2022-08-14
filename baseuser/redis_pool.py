import redis
from redis import ConnectionPool

REDIS_POOL = ConnectionPool(host='localhost', port=6379, max_connections=1000)
