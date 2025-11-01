#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, math
import utils
from led import PwmGPIO, LedPair


def main():

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
    led = LedPair(
        pin_a=12, 
        pin_b=13, 
        T_ramp=config["led"]["T_ramp"], 
        duty_a=0, 
        duty_b_factor=1/2, 
        f_pwm=frequency)
    
    try:
        #led.print_info()
        print("Setting PWM with frequency {} Hz and duty cycle {}%".format(frequency, duty_cycle))
        #led.set_pwm_a(duty_cycle_a=100)
        led.ramp_a(duty_start=duty_start, duty_end=duty_end)
        time.sleep(3)
        led.ramp_a(duty_start=duty_end, duty_end=duty_start)
        time.sleep(1)
        # led.ramp_b(duty_start=duty_start, duty_end=duty_end)
        led.ramp_b(duty_start=duty_start, duty_end=duty_end)
        time.sleep(3)
        led.ramp_b(duty_start=duty_end, duty_end=duty_start)
        time.sleep(1)



        #led.close()
        #print("LED closed.")
    finally:
        # Cleanup
        led.close()
        print("LED FINALLY closed.")

if __name__ == "__main__":
    main()