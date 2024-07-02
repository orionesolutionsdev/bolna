import redis
from pymongo import MongoClient
from config import settings
import motor.motor_asyncio
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")



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

def async_mongo_connection():
    """
    Establishes a connection to the MongoDB database using the environment variables 'MONGO_URL' and 'MONGO_DATABASE'.
    """
    try:
        async_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
        async_db = async_client[settings.MONGO_DATABASE]
    except ValueError as e:
        raise ValueError(f"Error in mongodb_connection: {e.args[0]}")
    return async_db



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


def create_s3_client():
    """Create an S3 client."""
    try:
        s3_client = boto3.client('s3', 
                                 region_name=AWS_REGION,
                                 aws_access_key_id=AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        return s3_client
    except NoCredentialsError:
        print("Credentials not available")
        return None
    except ClientError as e:
        print(f"ClientError during client creation: {e}")
        return None


def generate_presigned_url(s3_client, object_key):
    """Generate a pre-signed URL for the S3 object."""
    try:
        presigned_url = s3_client.generate_presigned_url('get_object',
                                                         Params={'Bucket': settings.RECORDING_BUCKET_NAME, 'Key': object_key},
                                                         ExpiresIn=3600)  # URL expires in 1 hour (3600 seconds)
        return presigned_url
    except ClientError as e:
        print(f"ClientError during URL generation: {e}")
        return None
    
def parse_s3_url(s3_url):
    """Extract bucket name and object key from the S3 URL."""
    if not s3_url.startswith("s3://"):
        raise ValueError("The URL is not a valid S3 URL")
    s3_path = s3_url[len("s3://"):]
    _, object_key = s3_path.split('/', 1)
    return  object_key


db = mongodb_connection()
redis_client = redis_connection()
async_db = async_mongo_connection()
s3_client = create_s3_client()