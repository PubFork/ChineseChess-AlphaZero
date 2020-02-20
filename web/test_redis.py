from json import JSONEncoder
import redis
import uuid
import json
from web.config import UserConfig, UserConfigEncoder


def save_and_read_by_standalone():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.set('name', 'junxi')
    print(r['name'])
    print(r.get('name'))
    print(type(r.get('name')))


def save_and_read_by_pool():
    pool = redis.ConnectionPool(host='localhost', port=6379,
                                decode_responses=True)
    r = redis.Redis(connection_pool=pool)
    r.set('gender', 'male')
    print(r.get('gender'))


def save_and_read_user_info():
    token = str(uuid.uuid1())
    pool = redis.ConnectionPool(host='localhost', port=6379,
                                decode_responses=True)
    r = redis.Redis(connection_pool=pool)
    print(UserConfigEncoder().encode(UserConfig(-1, token)))
    r.set(token, UserConfigEncoder().encode(UserConfig(-1, token)))
    print(r.get(token))
    r.delete(token)


save_and_read_user_info()
