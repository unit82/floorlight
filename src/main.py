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
from motion import PIRMotionSensor
# from gpiozero import MotionSensor

def main():

    # # Declaration of GPIO16 as an input for the PIR sensor
    # pir = MotionSensor(16)
    # # Intermediate variables
    # active = False
    # try:
    #     while True:
    #         # Monitoring changes from the PIR sensor
    #         if pir.motion_detected and not active:
    #             print("Motion detected")
    #             active = True
    #         elif not pir.motion_detected and active:
    #             print("No movement")
    #             active = False
    #         time.sleep(0.1)
    # # Termination condition
    # except KeyboardInterrupt:
    #     print("Program interrupted by user.")
    # finally:
    #     pir.close()

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
    # GPIO setup to BCM mode (explanation: https://pinout.xyz/pinout/bcm)
    GPIO.setmode(GPIO.BCM)
    # led = LedPair(
    #     pin_a=12, 
    #     pin_b=13, 
    #     T_ramp=config["led"]["T_ramp"], 
    #     duty_a=0, 
    #     duty_b_factor=1/4, 
    #     f_pwm=frequency)
    ms = PIRMotionSensor(pin=16, 
            led_pin_a=12, 
            led_pin_b=13, 
            led_T_ramp=config["led"]["T_ramp"], 
            led_duty_a=0, 
            led_duty_b_factor=1/4, 
            led_f_pwm=frequency)
    
    try:
        print("Starting motion sensor loop. Press Ctrl-C to exit.")
        ms.run_loop()
        print("Motion sensor loop ended.")
    finally:
        # Cleanup
        ms.close()
        print("Motion sensor closed.")

if __name__ == "__main__":
    main()