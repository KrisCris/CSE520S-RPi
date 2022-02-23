import time
from sensors import sensors
from messenger import messenger


# Callback when the subscribed topic receives a message
def on_message_received(code:int ,msg:str ,data:dict):
    inst = sensors.get_inst()
    if 'window' in data:
        if (data['window'] == True):
            inst.open_window()
        else:
            inst.close_window()


if __name__ == '__main__':
    try:
        conn = messenger(on_message_received=on_message_received)
        conn.connect()

        conn.subscribe('smart_window')


        inst = sensors.get_inst()

        while True:
            conn.send(topic="smart_window", code=1, msg='info', data={
                'dht': inst.get_temp_humid(),
                'isRaining': inst.is_rain(),
                # 'window': True
            })
            time.sleep(1)
            conn.send(topic="smart_window", code=1, msg='info', data={
                'dht': inst.get_temp_humid(),
                'isRaining': inst.is_rain(),
                # 'window': False
            })
            time.sleep(1)


    except KeyboardInterrupt:
        conn.disconnect()


