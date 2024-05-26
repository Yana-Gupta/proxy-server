import redis
import utils

def db_connection():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.flushall()
    
    r.sadd('filtering_keywords', *utils.keywords)

    print("Keywords added to Redis set successfully.")

    print("Connected to DB...... 🚀")
    return r
