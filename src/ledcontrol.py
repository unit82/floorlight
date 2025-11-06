#!/usr/bin/env python3
"""Simple motion sensor helper for the floorlight project.

Provides MotionSensor which waits for a rising edge on a GPIO input
and prints a message when motion is detected. The main loop is
interruptible with Ctrl-C (KeyboardInterrupt) and performs cleanup.
"""
from __future__ import annotations

from math import e
from socket import timeout
from gpiozero import MotionSensor
from led import LedPair
import math
import smbus
import bh1750
import time

class PIRMotionSensor:
    """Represent a PIR/motion sensor connected to a GPIO input.

    Usage:
        ms = MotionSensor(pin=16)
        ms.run_loop()

    The run_loop() method blocks in a while True loop and waits for a
    rising edge on the configured pin. On detection it prints a
    timestamped message. A KeyboardInterrupt stops the loop and calls
    close() to cleanup the GPIO for that pin.
    """

    def __init__(self, config: dict, pin: int = 16, led_pin_a: int = 12, led_pin_b: int = 13, led_duty_a: float = 0.0, led_duty_b_factor: float = 0.25):
        # GPIO setup to BCM mode (explanation: https://pinout.xyz/pinout/bcm)
        try:
            self.config = config
            # Motion sensor related parameters
            self.pin = int(pin)
            self.pir = MotionSensor(self.pin)

            # LED related parameters
            self.led_pin_a         = led_pin_a
            self.led_pin_b         = led_pin_b
            self.led_T_ramp        = config["led"]["T_ramp"]
            self.led_duty_a        = led_duty_a
            self.led_duty_b_factor = led_duty_b_factor
            self.led_f_pwm         = config["pwm"]["frequency"]
            self.led = LedPair(
                pin_a        =self.led_pin_a, 
                pin_b        =self.led_pin_b, 
                T_ramp       =self.led_T_ramp, 
                duty_a       =self.led_duty_a, 
                duty_b_factor=self.led_duty_b_factor, 
                f_pwm        =self.led_f_pwm)
            self.light_sensor = bh1750.BH1750()
        except Exception as e:
            print(f"Error initializing MotionSensor on pin {pin}: {e}")
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

    def run_loop(self, duty_start=0, duty_end=40, timeout=4.0, wait_for_motion_state=False, b_print_led=False, b_led_is_on=False) -> None:
        """Run a blocking loop that waits for motion and prints on detection.

        This method handles KeyboardInterrupt to allow clean exit via
        Ctrl-C. It uses GPIO.wait_for_edge which blocks efficiently.
        """
        try:
            while True:
                # Monitoring changes from the PIR sensor
                if self.pir.motion_detected:
                    # Measure light level
                    lux = self.light_sensor.read_lux()
                    print("Motion detected at lux value:", lux)
                    if b_led_is_on == False:
                        # Ramp up the LED strip
                        self.led.ramp_ab(duty_start=duty_start, duty_end=duty_end, b_print=b_print_led)
                        b_led_is_on = True
                    time.sleep(math.ceil(timeout/2))
                elif not self.pir.motion_detected :
                    # Wait for motion with timeout
                    wait_for_motion_state = self.pir.wait_for_motion(timeout=timeout*2)
                    # If wait_for_motion_state is True, leave this if-block
                    if wait_for_motion_state:
                        # A motion event occurred
                        print("wait_for_motion_state = True")
                        continue
                    else:
                        # No motion event within timeout
                        print("wait_for_motion_state = False")

                    if b_led_is_on and not wait_for_motion_state:
                        print("Turning off LED due to no motion.")
                        # Ramp down the LED strip
                        self.led.ramp_ab(duty_start=duty_end, duty_end=duty_start, b_print=b_print_led)
                        b_led_is_on = False
                time.sleep(0.1)
        # Termination condition
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
