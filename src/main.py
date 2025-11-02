''' 
Project:    Pi Floor Light

File:       src/main.py

Title:      Main Module for Pi Floor Light

Abstract:   This module serves as the main entry point for the Pi Floor Light project.
            It initializes the LED control using PWM signals on GPIO pins connected
            to IRLZ44NPBF MOSFETs controlling an LED strip. The module utilizes
            the RPi.GPIO library for GPIO management and PWM signal generation.

Author:     Dr. Oliver Opalko

Email:      oliver.opalko@gmail.com

'''

#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, math
import utils
from led import LedPair


def main():

    config = utils.load_config("./config/static_config.yaml")
    start_level = 0.001
    end_level = 1
    sleep_time = 1.0
    updates_ramp = 800
    dither_window = 20
    duration_ramp = 1.0
    duty_start = 0
    duty_end = 1
    # Load runtime configuration from config/settings.json (project root)
    duty_cycle = 5  # Duty cycle in percent
    frequency  = config["pwm"]["frequency"]   # Frequency in Hz
    # GPIO setup to BCM mode (explanation: https://pinout.xyz/pinout/bcm)
    GPIO.setmode(GPIO.BCM)
    led = LedPair(
        pin_a=12, 
        pin_b=13, 
        T_ramp=config["led"]["T_ramp"], 
        duty_a=0, 
        duty_b_factor=1/4, 
        f_pwm=frequency)
    
    try:
        #led.print_info()
        print("Setting PWM with frequency {} Hz and duty cycle {}%".format(frequency, duty_cycle))
        #led.set_pwm_a(duty_cycle_a=100)
        led.ramp_ab(duty_start=duty_start, duty_end=duty_end)
        time.sleep(2)
        led.ramp_ab(duty_start=duty_end, duty_end=duty_start)
        time.sleep(1)
        # led.ramp_a(duty_start=duty_start, duty_end=duty_end)
        # time.sleep(2)
        # led.ramp_a(duty_start=duty_end, duty_end=duty_start)
        # time.sleep(1)
        # # led.ramp_b(duty_start=duty_start, duty_end=duty_end)
        # led.ramp_b(duty_start=duty_start, duty_end=duty_end)
        # time.sleep(2)
        # led.ramp_b(duty_start=duty_end, duty_end=duty_start)
        # time.sleep(1)



        #led.close()
        #print("LED closed.")
    finally:
        # Cleanup
        led.close()
        print("LED FINALLY closed.")

if __name__ == "__main__":
    main()