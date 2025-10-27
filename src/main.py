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
    led0 = LedSoftPwmGPIO(pin=12, f_pwm=3000, gamma=1.1)
    led1 = LedSoftPwmGPIO(pin=13, f_pwm=3000, gamma=1.1)
    try:
        #led0.set_level(0.05, settle_ms=10)
        #time.sleep(3.0)
        led0.ramp(duration_s=5.0, start_level=0, end_level=0.01)
        time.sleep(3.0)
        led1.ramp(duration_s=5.0, start_level=0, end_level=0.01)
        #led1.ramp(duration_s=5.0, start_level=0.01, end_level=0.001)
        time.sleep(1.0)
        led0.ramp(duration_s=5.0, start_level=0.01, end_level=0.0)
        time.sleep(3.0)
        led1.ramp(duration_s=5.0, start_level=0.01, end_level=0.0)

        # Directly set to full brightness
        #led0.set_level(1, settle_ms=10)
        time.sleep(1.0)

        # Fade out
        led0.off()
        led1.off()

    finally:
        # Cleanup
        led0.close()
        led1.close()

if __name__ == "__main__":
    main()