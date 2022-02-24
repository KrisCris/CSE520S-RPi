import time
from sensors import sensors
from messenger import messenger


if __name__ == '__main__':
    try:
        conn = messenger()
        sensor_inst = sensors.get_inst()
        conn.connect()

        last_data = {
            "temperature": 24,
            "humidity": 50,
            "isRaining": False,
            "windowAngle": 0
        }

        def on_remote_control(payload: dict):
            conn.lock = True
            if payload.get("needOpen"):
                sensor_inst.open_window()
            else:
                sensor_inst.close_window()
            conn.send(topic="resume", payload={}, preempt=True)
            conn.lock = False

        conn.subscribe('remote_control', on_remote_control)

        def on_sync_request(payload: dict):
            topicId = payload.get("topicId")
            conn.send(topic=topicId, payload=last_data)

        conn.subscribe('sync_data', on_sync_request)
        
        # TODO Send info based on request
        while True:
            ret = sensor_inst.get_temp_humid()
            temp, humid = int(ret[0]), int(ret[1])
            is_rain = sensor_inst.is_rain()
            window_angle = sensor_inst.get_motor_angle()
            if temp != last_data['temperature'] \
                or humid != last_data['humidity'] \
                or is_rain != last_data['isRaining'] \
                or window_angle != last_data['windowAngle']:
                payload = {
                    'temperature': temp,
                    'humidity': humid,
                    'isRaining': is_rain,
                    'windowAngle': window_angle
                }
                last_data = payload
                conn.send(topic="boardcast", payload=payload)
            # time.sleep(0.1)

    except KeyboardInterrupt:
        conn.disconnect()
        sensor_inst.destroy()
