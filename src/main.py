#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, math
from led import LedPairSoftPwm

def main():
    start_level = 0.0
    end_level = 0.2
    sleep_time = 1.0
    # GPIO setup to BCM mode (explanation: https://pinout.xyz/pinout/bcm)
    GPIO.setmode(GPIO.BCM)
    # Use a single controller for both pins to avoid creating multiple
    # PWM objects on the same channel (RPi.GPIO raises an error then).
    leds = LedPairSoftPwm(pin_a=12, pin_b=13, f_pwm=3000, gamma=1.1)
    try:
        leds.ramp_both(duration_s=5.0, updates=400, dither_window=20,
                       start_a=start_level, end_a=end_level,
                       start_b=start_level, end_b=end_level)
        leds.set_levels(end_level, end_level, settle_ms=10)
        time.sleep(4.0)
        leds.ramp_both(duration_s=5.0, updates=400, dither_window=20,
                       start_a=end_level, end_a=0.0,
                       start_b=end_level, end_b=0.0)
        time.sleep(2.0)
        #led0.set_level(0.05, settle_ms=10)
        #time.sleep(3.0)
        # led0.ramp(duration_s=5.0, start_level=start_level, end_level=end_level)
        # time.sleep(sleep_time)
        # led1.ramp(duration_s=5.0, start_level=start_level, end_level=end_level)
        # #led1.ramp(duration_s=5.0, start_level=0.01, end_level=0.001)
        # time.sleep(sleep_time)
        # led0.ramp(duration_s=5.0, start_level=end_level, end_level=0.0)
        # time.sleep(sleep_time)
        # led1.ramp(duration_s=5.0, start_level=end_level, end_level=0.0)

        # Directly set to full brightness
        #led0.set_level(1, settle_ms=10)
        for i in range(10):
            time.sleep(sleep_time/10)
            # use the pair controller to set levels; here we only change A
            leds.set_levels(0.4, 0.0, settle_ms=10)
            time.sleep(sleep_time/10)
            leds.set_levels(0.6, 0.0, settle_ms=10)
        time.sleep(sleep_time)
        time.sleep(sleep_time)
        time.sleep(sleep_time)

        # Fade out
        leds.off()

    finally:
        # Cleanup
        leds.close()

if __name__ == "__main__":
    main()