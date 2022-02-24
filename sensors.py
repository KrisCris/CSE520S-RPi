import sys
import time
import RPi.GPIO as GPIO
import dht11
import json

import io
import json
import os


class sensors:
    inst = None
    pins = {
        "rain": 16,
        "dht": 21,
        "motor": [17, 22, 23, 24]
    }
    motor_seq = [
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1],
        [1, 0, 0, 1]
    ]
    dht11_inst = None

    serialized_data = {
        "motor_angle": 0,
        "last_success_read": [24, 50],
        "did_rain": False
    }
    
    fail_count = 0
    openAngle = 90
    closeAngle = 0


    def __init__(self) -> None:
        self.setup()
        self.load()
        sensors.inst = self


    def load(self):
        if os.path.isfile('sensor_data.json') and os.access('sensor_data.json', os.R_OK):
            # checks if file exists
            with open('sensor_data.json') as sensor_config:
                self.serialized_data = json.load(sensor_config)
        else:
            print ("Either file is missing or is not readable, creating file...")
            with io.open('sensor_data.json', 'w') as sensor_config:
                sensor_config.write(json.dumps(self.serialized_data))        

    
    @staticmethod
    def get_inst():
        if sensors.inst == None:
            sensors.inst = sensors()
        return sensors.inst


    def setup(self):
        GPIO.setmode(GPIO.BCM)
        self.dht11 = dht11.DHT11(pin=self.pins["dht"])

        GPIO.setup(self.pins["rain"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        for pin in self.pins['motor']:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)


    def is_rain(self):
        return not GPIO.input(self.pins["rain"])


    def run_motor(self, degree: int, direction=1):
        cycles = int((degree % 360) / 360 * 512)
        for _ in range(cycles):
            # 8 = len(motor_seq)
            for step in range(8):
                # 4 = # pins
                for pin in range(4):
                    GPIO.output(self.pins['motor'][pin],
                                self.motor_seq[step * direction][pin])
                time.sleep(0.001)
        # reset pins
        for pin in range(4):
            GPIO.output(self.pins['motor'][pin], 0)
        self.serialized_data['motor_angle'] = (self.serialized_data['motor_angle'] + degree * direction) % 360


    def get_motor_angle(self):
        return self.serialized_data['motor_angle']


    def open_window(self):
        angle = 90 - self.serialized_data["motor_angle"]
        print(angle)
        self.run_motor(degree=angle, direction=1)


    def close_window(self):
        # if ((self.serialized_data["motor_angle"] + 90) % 360 < 270):
        self.run_motor(degree=self.serialized_data["motor_angle"], direction=-1)


    def get_temp_humid(self):
        res = self.dht11.read()
        if not res.is_valid():
            self.fail_count += 1
            print(f"dht reading failed for {self.fail_count} time(s)")
            if self.fail_count > 60:
                return None, None
        else:
            self.serialized_data["last_success_read"][0], self.serialized_data["last_success_read"][1] = res.temperature, res.temperature
            self.fail_count = 0

        return self.serialized_data["last_success_read"][0], self.serialized_data["last_success_read"][1]
        


    def destroy(self):
        GPIO.cleanup()
        with io.open('sensor_data.json', 'w') as sensor_config:
            sensor_config.write(json.dumps(self.serialized_data))
