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

        ### Remote Control
        def on_remote_control(payload: dict):
            conn.lock = True
            if "angle" in payload:
                sensor_inst.rotate_window(payload.get("angle"))
                
            conn.send(topic="resume", payload={}, preempt=True)
            conn.lock = False
            

        conn.subscribe('remote_control', on_remote_control)
        ###


        ### Sync Data
        def on_sync_request(payload: dict):
            # topicId = payload.get("topicId")
            conn.send(topic="sync_end", payload=last_data, preempt=True)

        conn.subscribe('sync_start', on_sync_request)
        ###
        
        ### Update Data when Changed
        while True:
            ret = sensor_inst.get_temp_humid()
            temp, humid = int(ret[0]), int(ret[1])
            is_rain = sensor_inst.is_rain()
            window_angle = sensor_inst.get_motor_angle()

            if temp != last_data['temperature'] \
                or humid != last_data['humidity'] \
                or is_rain != last_data['isRaining'] \
                or window_angle != last_data['windowAngle']:

                if is_rain and is_rain != last_data['isRaining']:
                    sensor_inst.rotate_window(0)

                payload = {
                    'isRaining': is_rain,
                    'windowAngle': window_angle,
                    'temperature': temp,
                    'humidity': humid,
                }
                last_data = payload
                conn.send(topic="boardcast", payload=payload)

    except KeyboardInterrupt:
        conn.disconnect()
        sensor_inst.destroy()
