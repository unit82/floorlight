#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, math
from led import LedSoftPwmGPIO

def main():
    led = LedSoftPwmGPIO(pin=12, f_pwm=2000, gamma=1.1)
    try:

        led.ramp(duration_s=5.0, start_level=0.0, end_level=0.25)
        time.sleep(2.0)
        
        # 2 s von 0.5 → 1.0 (volle Helligkeit)
        led.ramp(duration_s=2.0, start_level=0.25, end_level=1.0)
        time.sleep(2.0)

        # 4 s von 1.0 → 0.2 (gedimmtes Ausklingen)
        led.ramp(duration_s=4.0, start_level=1.0, end_level=0.1)
        time.sleep(2.0)
        led.set_level(1, settle_ms=10)
        time.sleep(1.0)
        led.off()

    finally:
        led.close()

if __name__ == "__main__":
    main()