#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, math
from led import LedSoftPwmGPIO

def main():
    start_level = 0.0
    end_level = 0.3
    sleep_time = 1.0
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
        led0.ramp(duration_s=5.0, start_level=start_level, end_level=end_level)
        time.sleep(sleep_time)
        led1.ramp(duration_s=5.0, start_level=start_level, end_level=end_level)
        #led1.ramp(duration_s=5.0, start_level=0.01, end_level=0.001)
        time.sleep(sleep_time)
        led0.ramp(duration_s=5.0, start_level=end_level, end_level=0.0)
        time.sleep(sleep_time)
        led1.ramp(duration_s=5.0, start_level=end_level, end_level=0.0)

        # Directly set to full brightness
        #led0.set_level(1, settle_ms=10)
        for i in range(20):
            time.sleep(sleep_time/10)
            led0.set_level(0.4, settle_ms=10)
            time.sleep(sleep_time/10)
            led0.set_level(0.6, settle_ms=10)
        time.sleep(sleep_time)

        # Fade out
        led0.off()
        led1.off()

    finally:
        # Cleanup
        led0.close()
        led1.close()

if __name__ == "__main__":
    main()