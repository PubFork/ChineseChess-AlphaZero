import paho.mqtt.client as mqtt
import json
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("receive_topic_name")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1", 1883, 60)

response = {'id': 0, "current_x": 0, "current_y": 0, "target_x": 0, "target_y": 1,
                            "win": 1, "action": ""}

client.publish(topic="send_topic_name", payload=json.dumps(response), qos=0)

# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.