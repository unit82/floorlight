#!/usr/bin/env python3
"""
LED control for the floorlight project. 
Provides LEDControl which manages LED brightness based on motion
detection and ambient light levels. 
"""
from __future__ import annotations

import math
import time
# from socket import timeout
from gpiozero import MotionSensor
from led_pigpio import LedPair
from bh1750 import BH1750

class LEDControl:
    """Represent a PIR/motion sensor connected to a GPIO input.

    Usage:
        ms = MotionSensor(pin=16)
        ms.run_loop()

    The run_loop() method blocks in a while True loop and waits for a
    rising edge on the configured pin. On detection it prints a
    timestamped message. A KeyboardInterrupt stops the loop and calls
    close() to cleanup the GPIO for that pin.
    """

    def __init__(self, config: dict, led_duty_b_factor: float = 0.25):
        # GPIO setup to BCM mode (explanation: https://pinout.xyz/pinout/bcm)
        try:
            self.config = config
            # Motion sensor related parameters
            self.pir_pin = int(config["motion_sensor"]["pin"])
            self.pir     = MotionSensor(self.pir_pin)

            # LED related parameters
            self.led_pin_a         = config["led"]["pin_a"]
            self.led_pin_b         = config["led"]["pin_b"]
            self.led_T_ramp        = config["led"]["T_ramp"]
            self.led_duty_b_factor = led_duty_b_factor
            self.led_f_pwm         = config["pwm"]["frequency"]
            self.led = LedPair(
                config       =self.config,
                duty_b_factor=self.led_duty_b_factor)
            self.light_sensor = BH1750(lux_max=config["light_sensor"]["shut_down_at_lux"])
            time.sleep(1)
        except Exception as e:
            print(f"Error initializing MotionSensor: {e}")
            raise

    #########################################################
    # Private Helper Methods
    #########################################################

    def _wait_for_settled_pir(self) -> None:
        # Loop until PIR output is 0
        while self.pir.motion_detected:
            time.sleep(0.1)


    #########################################################
    # Public Methods
    #########################################################

    def light_on_motion(self, duty_start=0, duty_end=40, timeout=4.0, b_led_is_on=False, b_print_led=True) -> None:
        """
        Turn on the LED strip on motion detection, then turn off after timeout.
        """
        if self.pir.motion_detected:
            # Measure light level
            lux = self.light_sensor.read_lux()
            print("Motion detected at lux value: {:.4f}".format(lux))
            if b_led_is_on == False:                
                self.led.ramp_ab( # Ramp up the LED strip
                    duty_start=duty_start, duty_end=duty_end, b_print=b_print_led)
                b_led_is_on = True
            time.sleep(math.ceil(timeout/2))
            return b_led_is_on
        elif not self.pir.motion_detected :
            wait_for_motion_state = self.pir.wait_for_motion(timeout=timeout*2)
            if wait_for_motion_state:
                print("A motion event occurred: wait_for_motion_state = True")
                return b_led_is_on
            else:
                print("No motion event within timeout: wait_for_motion_state = False")

            if b_led_is_on and not wait_for_motion_state:
                print("Turning off LED due to no motion.")
                self.led.ramp_ab( # Ramp down the LED strip
                    duty_start=duty_end, duty_end=duty_start, b_print=b_print_led)
                b_led_is_on = False
            return b_led_is_on

    def light_on_motion_loop(self, duty_start=0, duty_end=40, timeout=4.0, b_led_is_on=False, b_print_led=False) -> None:
        """
        Run a blocking loop that waits for motion and prints on detection.

        This method handles KeyboardInterrupt to allow clean exit via
        Ctrl-C. It uses GPIO.wait_for_edge which blocks efficiently.
        """
        try:
            b_led_is_on = False
            while True:
                b_led_is_on = self.light_on_motion(duty_start, duty_end, timeout, b_led_is_on=b_led_is_on, b_print_led=b_print_led)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Program interrupted by user.")
        finally:
            self.close()

    def light_on_motion_lux_loop(self, duty_start=0, duty_end=40, timeout=4.0, b_led_is_on=False, b_print_led=True) -> None:
        try:
            b_led_is_on = False
            while True:
                if not b_led_is_on:
                    duty_end_dynamic = self.light_sensor.lux_to_duty_cycle(self.light_sensor.read_lux())
                    print("####### LED is off. Based on lux Dynamic duty_end:", duty_end_dynamic)
                b_led_is_on = self.light_on_motion(duty_start, duty_end_dynamic, timeout, b_led_is_on=b_led_is_on, b_print_led=b_print_led)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Program interrupted by user.")
        finally:
            self.close()

    def close(self) -> None:
        """Cleanup only the pin used by this sensor.

        We avoid calling GPIO.cleanup() without arguments because that
        might remove other pins used by the program. Cleanup only the
        sensor pin for safety.
        """
        try:
            self.pir.close()
            self.led.close()
            self.light_sensor.power_down()
        except Exception:
            # best-effort cleanup; ignore errors
            pass

    #########################################################
    # Debug related Methods
    #########################################################

    def debug_print_motion_detected(self) -> None:
        """Print a message indicating motion was detected."""
        try:
            while True:
                self.pir.wait_for_motion()
                print(f"Motion detected at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                self.pir.wait_for_no_motion()
                print(f"No motion at       {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except KeyboardInterrupt:
            print("Program interrupted by user.")

    def debug_turn_led_on_2_seconds(self, duty_cycle=50) -> None:
        """Turn on the LED for 2 seconds for debugging."""
        try:
            print("Turning on LED for 2 seconds at duty cycle {}%".format(duty_cycle))
            self.led.set_pwm_a(duty_cycle)
            time.sleep(2)
            self.led.set_pwm_a(0)
            print("LED turned off.")
        except KeyboardInterrupt:
            print("Program interrupted by user.")
