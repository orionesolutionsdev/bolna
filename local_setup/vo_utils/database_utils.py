import redis
from pymongo import MongoClient
from config import settings




def redis_connection():
    """
    Establishes a connection to the Redis database using the environment variable 'REDIS_URL'.
    """
    try:
        redis_pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client = redis.Redis.from_pool(redis_pool)
        return redis_client
    except ValueError as e:

        raise ValueError(f"Error in redis_connection: {e.args[0]}")


def mongodb_connection():
    """
    Establishes a connection to the MongoDB database using the environment variables 'MONGO_URL' and 'MONGO_DATABASE'.
    """
    try:
        mongo_client = MongoClient(settings.MONGODB_URI)
        db = mongo_client[settings.MONGO_DATABASE]
    except ValueError as e:
        raise ValueError(f"Error in mongodb_connection: {e.args[0]}")
    return db

db = mongodb_connection()
redis_client = redis_connection()