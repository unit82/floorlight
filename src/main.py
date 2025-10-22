#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, math
from led import LedSoftPwmGPIO

def main():
    # GPIO setup to BCM mode (explanation: https://pinout.xyz/pinout/bcm)
    GPIO.setmode(GPIO.BCM)
    # GPIO setup for the LED pins
    GPIO.setup(12, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    led0 = LedSoftPwmGPIO(pin=12, f_pwm=2000, gamma=1.1)
    led1 = LedSoftPwmGPIO(pin=13, f_pwm=2000, gamma=1.1)
    try:

        led0.ramp(duration_s=5.0, start_level=0.0, end_level=0.25)
        time.sleep(2.0)
        led1.ramp(duration_s=5.0, start_level=0.0, end_level=0.25)
        
        # 2 s from 25% to 100%
        led0.ramp(duration_s=2.0, start_level=0.25, end_level=1.0)
        time.sleep(2.0)

        # 4 s from 1.0 to 0.1
        led0.ramp(duration_s=4.0, start_level=1.0, end_level=0.1)
        time.sleep(2.0)

        # Directly set to full brightness
        led0.set_level(1, settle_ms=10)
        time.sleep(1.0)
        led0.off()

    finally:
        # Cleanup
        led0.close()
        led1.close()

if __name__ == "__main__":
    main()