import time
import paho.mqtt.client as mqtt
from logging import getLogger
import redis

logger = getLogger(__name__)


class NetWorkConnectionConfig:
    def __init__(self):
        self.mqtt_ip = "127.0.0.1"
        self.mqtt_port = 1883
        self.mqtt_keepalive = 60
        self.mqtt_receive_topic_name = "receive_topic_name"
        self.mqtt_send_topic_name = "send_topic_name"
        self.mqtt_listener_name = "listener_name"

        self.redis_ip = "localhost"
        self.redis_port = 6379


class NetWorkConnection:
    def __init__(self):
        self.start_time = time.time()
        self.network_connection_config = NetWorkConnectionConfig()

    def get_message_queue_client(self, on_connect_func, on_message_func):
        logger.debug(f"the network helper has been init at: {self.start_time} ")
        client = mqtt.Client()
        client.on_connect = on_connect_func
        client.on_message = on_message_func
        client.connect(self.network_connection_config.mqtt_ip,
                       self.network_connection_config.mqtt_port,
                       self.network_connection_config.mqtt_keepalive)
        return client

    def get_redis_client(self):
        pool = redis.ConnectionPool(host=self.network_connection_config.redis_ip,
                                    port=self.network_connection_config.redis_port,
                                    decode_responses=True)
        redis_client = redis.Redis(connection_pool=pool)
        return redis_client
