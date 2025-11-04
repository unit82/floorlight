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

    def __init__(self, pin: int = 16):
        try:
            self.pin = int(pin)
            self.pir = MotionSensor(self.pin)
        except Exception as e:
            print(f"Error initializing MotionSensor on pin {pin}: {e}")
            raise
    
    def run_loop(self) -> None:
        """Run a blocking loop that waits for motion and prints on detection.

        This method handles KeyboardInterrupt to allow clean exit via
        Ctrl-C. It uses GPIO.wait_for_edge which blocks efficiently.
        """
        # Intermediate variables
        active = False

        try:
            while True:
                # Monitoring changes from the PIR sensor
                if self.pir.motion_detected and not active:
                    print("Motion detected")
                    active = True
                elif not self.pir.motion_detected and active:
                    print("No movement")
                    active = False

                time.sleep(0.1)

        # Termination condition
        except KeyboardInterrupt:
            print("Program interrupted by user.")

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
