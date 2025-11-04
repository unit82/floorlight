#!/usr/bin/env python3
"""Simple motion sensor helper for the floorlight project.

Provides MotionSensor which waits for a rising edge on a GPIO input
and prints a message when motion is detected. The main loop is
interruptible with Ctrl-C (KeyboardInterrupt) and performs cleanup.
"""
from __future__ import annotations

import time
from gpiozero import MotionSensor
from led import LedPair


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

    def __init__(self, pin: int = 16, led_pin_a: int = 12, led_pin_b: int = 13, led_T_ramp: float = 5.0, led_duty_a: float = 0.0, led_duty_b_factor: float = 0.25, led_f_pwm: float = 1000.0):
        try:
            # Motion sensor related parameters
            self.pin = int(pin)
            self.pir = MotionSensor(self.pin)

            # LED related parameters
            self.led_pin_a         = led_pin_a
            self.led_pin_b         = led_pin_b
            self.led_T_ramp        = led_T_ramp
            self.led_duty_a        = led_duty_a
            self.led_duty_b_factor = led_duty_b_factor
            self.led_f_pwm         = led_f_pwm
            self.led = LedPair(
                pin_a        =self.led_pin_a, 
                pin_b        =self.led_pin_b, 
                T_ramp       =self.led_T_ramp, 
                duty_a       =self.led_duty_a, 
                duty_b_factor=self.led_duty_b_factor, 
                f_pwm        =self.led_f_pwm)
        except Exception as e:
            print(f"Error initializing MotionSensor on pin {pin}: {e}")
            raise
    
    def run_loop(self) -> None:
        """Run a blocking loop that waits for motion and prints on detection.

        This method handles KeyboardInterrupt to allow clean exit via
        Ctrl-C. It uses GPIO.wait_for_edge which blocks efficiently.
        """
        # Intermediate variables
        active     = False
        duty_start = 0
        duty_end   = 50
        try:
            while True:
                # Monitoring changes from the PIR sensor
                if self.pir.motion_detected and not active:
                    print("Motion detected")
                    active = True
                    # use the instance's LedPair controller
                    self.led.ramp_ab(duty_start=duty_start, duty_end=duty_end)
                    time.sleep(5)
                elif not self.pir.motion_detected and active:
                    print("No movement")
                    time.sleep(2)
                    self.led.ramp_ab(duty_start=duty_end, duty_end=duty_start)
                    active = False

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
        except Exception:
            # best-effort cleanup; ignore errors
            pass
