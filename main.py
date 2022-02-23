from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import time
from uuid import uuid4

import sensors
from motor import motor
from messenger import messenger


# Callback when the subscribed topic receives a message
def on_message_received(code:int ,msg:str ,data:dict):
    if 'window' in data and data['window'] == True:
          motor(1,-1)


if __name__ == '__main__':
    try:
        conn = messenger(on_message_received=on_message_received)
        conn.connect()

        conn.subscribe('smart_window')


        sensors.setup()

        while True:
            conn.send(topic="smart_window", code=1, msg='info', data={
                'dht': sensors.getTempHumid(),
                'isRaining': sensors.isRaining(),
                'window': True
            })
            time.sleep(1)


    except KeyboardInterrupt:
        conn.disconnect()

