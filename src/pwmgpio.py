''' 
Project:    Pi Floor Light

File:       src/pwmgpio.py

Title:      PWM GPIO Control for Raspberry Pi

Abstract:   This module provides a class for controlling PWM signals on GPIO pins which            
            are connected to IRLZ44NPBF MOSFETs to a LED strip. The GPIO pins are
            connected to the gate of the MOSFETs (left leg), allowing for brightness control
            of the LED strips via PWM signals.

            The module uses the RPi.GPIO library to manage the GPIO pins and generate PWM signals.

Author:     Dr. Oliver Opalko

Email:      oliver.opalko@gmail.com

'''
#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, math
import utils

###################################################
# LED PWM Control
###################################################
class PwmGPIO:
    """Class for controlling an LED via software PWM on two GPIO pins.
    Uses dithering to achieve smooth brightness levels."""
    def __init__(self, pin, f_pwm=2000):
        self.pin = pin
        self.f_pwm = f_pwm           # 2 kHz is a good default
        # GPIO setup
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, self.f_pwm)

        # Initialize PWM with 0% duty cycle
        self.pwm.start(0.0)

    # Methode to control the PWM signal (period and duty cycle)
    def set_pwm(self, frequency, duty_cycle):
        self.pwm.ChangeFrequency(frequency)
        self.pwm.ChangeDutyCycle(duty_cycle)

    def stop(self):
        """Stop PWM."""
        self.pwm.stop()

    def close(self):
        """Cleanup GPIO and stop PWM."""
        try:
            # Stop PWM
            self.pwm.stop()
        finally:
            # Cleanup GPIO
            GPIO.cleanup([self.pin])
            