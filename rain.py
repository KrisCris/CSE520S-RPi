#!/usr/bin/python
# encoding:utf-8
from motor import motor
import RPi.GPIO as GPIO
import time
def detect():
    pin_rain=16
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_rain, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    isOpen = True
    try:
        while True:
            status = GPIO.input(pin_rain)
            if status == False and isOpen:
                motor(1,-1)
                isOpen = not isOpen
            else:
                print(1)
            time.sleep(0.5)
    except KeyboradInterrupt:
        GPIO.cleanup()


if __name__ == "__main__":
    detect()