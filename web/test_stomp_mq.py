import stomp
import time
import json


receive_topic_name = 'receive_topic_name'
send_topic_name = 'send_topic_name'

listener_name = 'receive_topic_name_listener'


queue_name = 'demo'
# topic_name = 'demo'
# listener_name = 'demo'


class SampleListener(object):
    def on_message(self, headers, message):
        print('headers: %s' % headers)
        print('message: %s' % message)


# 推送到队列queue
def send_to_queue(msg):
    conn = stomp.Connection10([('127.0.0.1', 61613)])
    conn.connect()
    conn.send(queue_name, msg)
    conn.disconnect()


# 推送到主题
def send_to_topic(msg):
    conn = stomp.Connection10([('127.0.0.1', 61613)])
    conn.connect()
    # conn.send("send_topic_name", msg)
    while 1:
        conn.send("receive_topic_name", msg)
        time.sleep(3)  # secs
    conn.disconnect()


##从队列接收消息
def receive_from_queue():
    conn = stomp.Connection10([('127.0.0.1', 61613)])
    conn.set_listener(listener_name, SampleListener())
    conn.connect()
    conn.subscribe(queue_name)
    time.sleep(1)  # secs
    conn.disconnect()


##从主题接收消息
def receive_from_topic():
    conn = stomp.Connection10([('127.0.0.1', 61613)])
    conn.set_listener(listener_name, SampleListener())
    conn.connect()
    conn.subscribe("receive_topic_name")
    while 1:
        # send_to_topic('topic')
        time.sleep(3)  # secs
    conn.disconnect()

class UserEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ActionResponse):
            return obj.name


class ActionResponse(object):
    def __init__(self):
        self.id = 0
        self.current_x = 0
        self.current_y = 0
        self.target_x = 0
        self.target_y = 0

if __name__ == '__main__':
    data = {'id': -1, "current_x": 0, "current_y": 1, "target_x": 0, "target_y": 0}
    # send_to_topic(json.dumps(data))
    # receive_from_queue()
    receive_from_topic()