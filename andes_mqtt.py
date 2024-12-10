import json
import time

from paho.mqtt import client as MQTT

broker_address = "10.20.1.227"
port = 1883
topic = "ACET/image/payload"


class MQTTSend:
    def send_data():
        with open("CompressAllPhoto.json") as f:
            data = json.load(f)
        payload = data["base64_data"]
        splitNum = 50
        datalen = len(payload)
        strlen = (datalen // splitNum) + 1

        for i in range(splitNum):
            client = MQTT.Client()
            client.connect(broker_address, port, 300)
            message = {
                "part": i + 1,
                "total_parts": splitNum,
                "data": payload[i * strlen : (i + 1) * strlen],
            }
            client.publish(topic, json.dumps(message), 1)
            time.sleep(0.5)
            client.disconnect()
