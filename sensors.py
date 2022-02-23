import sys
import time
import RPi.GPIO as GPIO
import dht11


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

    def __init__(self) -> None:
        self.setup()
        sensors.inst = self

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
        return GPIO.input(self.pins["rain"]) == False

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

    def open_window(self):
        self.run_motor(degree=90, direction=1)

    def close_window(self):
        self.run_motor(degree=90, direction=-1)

    def get_temp_humid(self):
        res = self.dht11.read()
        if res.is_valid():
            return res.temperature, res.humidity
        else:
            return False

    def destroy(self):
        GPIO.cleanup()
