import sys
import time
import RPi.GPIO as GPIO
import dht11

pins = {
    "rain":16,
    "dht":21,
    "motor":[17,22,23,24]
}

dht11_inst = None

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
    global dht11_inst
    dht11_inst = dht11.DHT11(pin=pins["dht"])
    GPIO.setup(pins["rain"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    

def isRaining():
    return GPIO.input(pins["rain"]) == False


def openWindow():
    pass


def closeWindow():
    pass


def testMotor():
    pass


def getTempHumid():
    global dht11_inst
    res = dht11_inst.read()
    if res.is_valid():
        return res.temperature, res.humidity
    else:
        return False


if __name__ == "__main__":
    setup()
    while(True):
        res = getTempHumid()
        if res:
            print(f"temp={res[0]}, humid={res[1]}")
            print(f"raining? {isRaining()}")
    