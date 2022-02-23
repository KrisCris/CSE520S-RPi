import time
from sensors import sensors
from messenger import messenger


if __name__ == '__main__':
    try:
        conn = messenger()
        sensor_inst = sensors.get_inst()

        conn.connect()

        def on_window_action(code: int, msg: str, data: dict):
            if 'window' in data:
                if (data['window'] == True):
                    sensor_inst.open_window()
                else:
                    sensor_inst.close_window()
        conn.subscribe('smart_window', on_window_action)

        while True:
            conn.send(topic="smart_window", code=1, msg='info', data={
                'dht': sensor_inst.get_temp_humid(),
                'isRaining': sensor_inst.is_rain(),
                'window': True
            })
            time.sleep(1)
            conn.send(topic="smart_window", code=1, msg='info', data={
                'dht': sensor_inst.get_temp_humid(),
                'isRaining': sensor_inst.is_rain(),
                'window': False
            })
            time.sleep(1)

    except KeyboardInterrupt:
        conn.disconnect()
        sensor_inst.destroy()
