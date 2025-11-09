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
import time, math
import utils
import ledcontrol
from led_pigpio import LedPair
# from gpiozero import MotionSensor

def main():

    """Main function to initialize and control the LED strip via PWM."""
    config = utils.load_config("./config/static_config.yaml")
 
    # Load runtime configuration from config/settings.json (project root)
    duty_cycle = 5  # Duty cycle in percent
    frequency  = config["pwm"]["frequency"]   # Frequency in Hz

    led_ctrl = ledcontrol.LEDControl(
            config=config,
            pin=16, 
            led_pin_a=12, 
            led_pin_b=13, 
            led_duty_a=0, 
            led_duty_b_factor=1/4)
    led = LedPair(
            pin_a=12,
            pin_b=13,
            T_ramp=2.0,
            duty_a=0,
            duty_b_factor=1/256,
            f_pwm=200
    )
    try:
        # led.ramp_ab(duty_start, duty_end, b_print=True)
        # led.ramp_ab(duty_end, duty_start, b_print=True)
        
        led_ctrl.light_on_motion_lux_loop()
        print("LED control loop ended.")
    finally:
        # Cleanup
        led_ctrl.close()
        led.close()
        print("LED control closed.")

if __name__ == "__main__":
    main()
    