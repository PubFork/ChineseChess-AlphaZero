import time
from json import JSONEncoder
import json


class UserConfigEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, UserConfig):
            return object.__dict__
        else:
            # call base class implementation which takes care of
            # raising exceptions for unsupported types
            return json.JSONEncoder.default(self, object)


class UserConfig:
    def __init__(self, id, user_name=None, password=None, token=None):
        self.id = id
        self.user_name = user_name
        self.last_update_time = time.time()
        self.token = token
        self.password = password
