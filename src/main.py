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
import ledcontrol
from led import LedPair
# from gpiozero import MotionSensor

def main():

    """Main function to initialize and control the LED strip via PWM."""
    config = utils.load_config("./config/static_config.yaml")
    start_level = 0.001
    end_level = 1
    sleep_time = 1.0
    updates_ramp = 800
    dither_window = 20
    duration_ramp = 1.0
    duty_start = 0
    duty_end = 10
    # Load runtime configuration from config/settings.json (project root)
    duty_cycle = 5  # Duty cycle in percent
    frequency  = config["pwm"]["frequency"]   # Frequency in Hz

    ms = ledcontrol.LEDControl(
            config=config,
            pin=16, 
            led_pin_a=12, 
            led_pin_b=13, 
            led_duty_a=0, 
            led_duty_b_factor=1/4)
    
    try:
        print("Starting motion sensor loop. Press Ctrl-C to exit.")
        # ms.debug_print_motion_detected()
        ms.run_loop()
        print("Motion sensor loop ended.")
    finally:
        # Cleanup
        ms.close()
        print("Motion sensor closed.")

if __name__ == "__main__":
    main()