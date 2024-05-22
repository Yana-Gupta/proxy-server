import redis

def db_connection():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    print("Connected to DB...... 🚀")
    return r
