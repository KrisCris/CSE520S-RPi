import time
from sensors import sensors
from messenger import messenger


if __name__ == '__main__':
    try:
        conn = messenger()
        sensor_inst = sensors.get_inst()

        conn.connect()

        def on_remote_control(payload: dict):
            conn.lock = True
            if payload.get("needOpen"):
                sensor_inst.open_window()
            else:
                sensor_inst.close_window()
            conn.send(topic="resume", payload={}, preempt=True)
            conn.lock = False

        conn.subscribe('forceAction', on_remote_control)

        def on_sync_request(payload: dict):
            topicId = payload.get("topicId")
            conn.send(topic="smart_window", payload={
                'code':1,
                'msg':'info',
                'temperature': ret[0],
                'humidity': ret[1],
                'isRaining': sensor_inst.is_rain(),
                'windowAngle': sensor_inst.get_motor_angle()
            })
        
        # TODO Send info based on request
        while True:
            ret = sensor_inst.get_temp_humid()
            conn.send(topic="smart_window", payload={
                'code':1,
                'msg':'info',
                'temperature': ret[0],
                'humidity': ret[1],
                'isRaining': sensor_inst.is_rain(),
                'windowAngle': sensor_inst.get_motor_angle()
            })
            time.sleep(0.5)

    except KeyboardInterrupt:
        conn.disconnect()
        sensor_inst.destroy()
