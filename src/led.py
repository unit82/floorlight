''' 
Project:    Pi Floor Light

File:       src/led.py

Title:      LED Control for Raspberry Pi

Abstract:   This module provides a class for controlling LED strips via PWM signals on GPIO pins.
            It utilizes the PwmGPIO class to manage the PWM signals and achieve smooth brightness
            levels through dithering.

            The brightness of the LEDs is controlled by adjusting the duty cycle of the PWM signals
            and the frequency. The duty cycle's range is from 0% (off) to 100% (fully on), where
            higher duty cycles correspond to brighter LED output. The frequency determines how fast
            the PWM signal is switched on and off, affecting the perceived brightness and smoothness
            of the LED dimming.

Author:     Dr. Oliver Opalko

Email:      oliver.opalko@gmail.com

'''
#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, math
import utils
from pwmgpio import PwmGPIO


######################################################################################################
# LED Pair Control
######################################################################################################
class LedPair:
    """Class for controlling a pair of LEDs via software PWM on two GPIO pins.
    Uses dithering to achieve smooth brightness levels. The duty cycle controls the brightness
    of the LEDs.
    
    Parameters:
        pin_a (int): GPIO pin for LED A.
        pin_b (int): GPIO pin for LED B.
        T_ramp (float): Ramp time in seconds.
        duty_a (float): Initial duty cycle for LED A (percent).
        duty_b_factor (float): Factor to determine duty cycle for LED B relative to LED A
        f_pwm (float): PWM frequency in Hz.
    """
    def __init__(self, pin_a=12, pin_b=13, T_ramp=2.0, duty_a=0, duty_b_factor=1/2, f_pwm=200):
        # Public attributes
        self.pin_a  = pin_a
        self.pin_b  = pin_b
        self.T_ramp = T_ramp         # Ramp time in seconds
        self.duty_a = float(duty_a)  # Initial duty cycle for LED A (percent)
        self.duty_b = self.duty_a * self._clamp_duty_b_factor(duty_b_factor) 
        self.duty_b_factor = self._clamp_duty_b_factor(duty_b_factor)
        self.f_pwm  = f_pwm  # 200 Hz is a good default

        # Private attributes (Constants)
        self._N_duty = 101 # Number of duty cycle steps
        self._T_duty = self.T_ramp / (2*self._N_duty)
        self._N_x = 2
        self._X_duty = self._N_x * self._N_duty

        # GPIO setup
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_a, GPIO.OUT)
        GPIO.setup(self.pin_b, GPIO.OUT)
        self.led_a = PwmGPIO(pin=self.pin_a, f_pwm=self.f_pwm*1000)
        self.led_b = PwmGPIO(pin=self.pin_b, f_pwm=self.f_pwm*1000)

        # Initialize PWM with the computed duty cycles
        self.led_a.set_pwm(self.f_pwm, self.duty_a)
        self.led_b.set_pwm(self.f_pwm, self.duty_b)

    #########################################################
    # Private Helper Methods
    #########################################################
    def _clamp_duty_b_factor(self, duty_b_factor):
        """ Clamp duty_b_factor to be within [0.01, 1.0].
        Returns:
            float: Clamped duty_b_factor.
        """
        if duty_b_factor < 0.01:
            return 0.01
        elif duty_b_factor > 1.0:
            return 1.0
        return duty_b_factor
    
    def _get_n_duty(self, duty_start, duty_end):
        """Calculate the number of duty cycle steps
        between duty_start and duty_end.
        Returns:
            int: Number of duty cycle steps.
        """
        if duty_start < duty_end:
            return abs(int((duty_end - duty_start)+1))
        else:
            return abs(int((duty_start - duty_end)+1))
    
    def _get_x_duty(self, n_duty, b_print=True):
        # Return ceil(2*_N_duty/n_duty)
        x_duty_float = 2*self._N_duty/n_duty
        x_duty = math.ceil(x_duty_float)
        if b_print:
            print("_N_duty: {}, n_duty: {}, x_duty_float: {}".format(self._N_duty, n_duty, x_duty_float))
            print("Calculating x_duty = ceil(2*{}/{})) = ceil({}) = {}".format(self._N_duty, n_duty, x_duty_float, x_duty))
        return x_duty

    def _get_vector_duty(self, duty_start, duty_end):
        """Generate a duty cycle vector for ramping."""
        # The vector is as follows (Matlab notation): (duty_start:duty_end). It
        # creates first a vector with a range from duty_start to duty_end. It works
        # for both increasing and decreasing ramps: duty_start > duty_end and vice versa.
        if duty_start < duty_end:
            vector_duty = list(range(int(duty_start), int(duty_end)+1))
        else:
            vector_duty = list(range(int(duty_start), int(duty_end)-1, -1))
        return vector_duty
    
    def _get_vector_duty_resample(self, x_duty, vector_duty, duty_end):
        """Resample the duty cycle vector to match x_duty steps."""
        # Every element in vector_duty is repeated x_duty times
        vector_duty_resampled = []
        for duty in vector_duty:
            vector_duty_resampled.extend([duty] * x_duty)
        # Trim the resampled vector to not exceed self._X_duty
        vector_duty_resampled_trimmed = vector_duty_resampled[:self._X_duty]
        # Force the last element to be duty_end
        vector_duty_resampled_trimmed[-1] = duty_end
        # Return the resampled vector
        return vector_duty_resampled_trimmed
    
    def _get_vector_duty_resample_ab(self, duty_start, duty_end, b_print=True):
        duty_start_a = duty_start
        duty_end_a   = duty_end
        duty_start_b = duty_start * self.duty_b_factor
        duty_end_b   = duty_end * self.duty_b_factor
        n_duty_a = self._get_n_duty(duty_start_a, duty_end_a)
        n_duty_b = self._get_n_duty(duty_start_b, duty_end_b)
        x_duty_a = self._get_x_duty(n_duty_a, b_print=b_print)
        x_duty_b = self._get_x_duty(n_duty_b, b_print=b_print)
        vector_duty_a = self._get_vector_duty(duty_start_a, duty_end_a)
        vector_duty_b = self._get_vector_duty(duty_start_b, duty_end_b)
        vector_duty_resampled_a = self._get_vector_duty_resample(x_duty_a, vector_duty_a, duty_end_a)
        vector_duty_resampled_b = self._get_vector_duty_resample(x_duty_b, vector_duty_b, duty_end_b)
        if b_print:
            print("Ramping LED A and B from {}% to {}% over {} seconds: n_duty = {}, x_duty = {}".format(duty_start, duty_end, self.T_ramp, n_duty_a , x_duty_a))
            print("N_duty: {}, n_duty: {}, X_duty: {}".format(self._N_duty, n_duty_a, x_duty_a))
            print("Duty Vector (length: {}) for ramping LED A and B: {}".format(len(vector_duty_a), vector_duty_a))
            print("Resampled Duty Vector (length: {}) for ramping LED A and B: {}".format(len(vector_duty_resampled_a),  vector_duty_resampled_a))
        return vector_duty_resampled_a, vector_duty_resampled_b

    #########################################################
    # Public Methods
    #########################################################

    def ramp_a(self, duty_start, duty_end):
        """Ramp both LEDs from duty_start to duty_end over T_ramp seconds."""
        n_duty = self._get_n_duty(duty_start, duty_end)
        x_duty = self._get_x_duty(n_duty)
        vector_duty = self._get_vector_duty(duty_start, duty_end)
        vector_duty_resampled = self._get_vector_duty_resample(x_duty, vector_duty, duty_end)
        print("Ramping LED A from {}% to {}% over {} seconds: n_duty = {}, x_duty = {}".format(duty_start, duty_end, self.T_ramp, n_duty , x_duty))
        print("N_duty: {}, n_duty: {}, X_duty: {}".format(self._N_duty, n_duty, x_duty))
        print("Duty Vector (length: {}) for ramping LED A: {}".format(len(vector_duty), vector_duty))
        print("Resampled Duty Vector (length: {}) for ramping LED A: {}".format(len(vector_duty_resampled),  vector_duty_resampled))
        for duty in vector_duty_resampled:
            self.led_a.set_pwm(self.f_pwm, duty)
            #print("Setting LED A duty to {}%".format(duty))
            time.sleep(self._T_duty)

    def ramp_b(self, duty_start, duty_end):
        """Ramp both LEDs from duty_start to duty_end over T_ramp seconds."""
        n_duty = self._get_n_duty(duty_start, duty_end)
        x_duty = self._get_x_duty(n_duty)
        vector_duty = self._get_vector_duty(duty_start, duty_end)
        vector_duty_resampled = self._get_vector_duty_resample(x_duty, vector_duty, duty_end)
        print("Ramping LED B from {}% to {}% over {} seconds: n_duty = {}, x_duty = {}".format(duty_start, duty_end, self.T_ramp, n_duty , x_duty))
        print("N_duty: {}, n_duty: {}, X_duty: {}".format(self._N_duty, n_duty, x_duty))
        print("Duty Vector (length: {}) for ramping LED B: {}".format(len(vector_duty), vector_duty))
        print("Resampled Duty Vector (length: {}) for ramping LED B: {}".format(len(vector_duty_resampled),  vector_duty_resampled))
        for duty in vector_duty_resampled:
            self.led_b.set_pwm(self.f_pwm, duty)
            #print("Setting LED B duty to {}%".format(duty))
            time.sleep(self._T_duty)
    

    def ramp_ab(self, duty_start, duty_end, b_print=True):
        """Ramp both LEDs from duty_start to duty_end over T_ramp seconds."""
        vector_duty_resampled_a, vector_duty_resampled_b = self._get_vector_duty_resample_ab(duty_start, duty_end, b_print=b_print)
        for i in range(len(vector_duty_resampled_a)):
            duty_a = vector_duty_resampled_a[i]
            duty_b = vector_duty_resampled_b[i]
            self.led_a.set_pwm(self.f_pwm, duty_a)
            self.led_b.set_pwm(self.f_pwm, duty_b)
            #print("Setting LED A duty to {}% and LED B duty to {}%".format(duty_a, duty_b))
            time.sleep(self._T_duty)

    def set_pwm_a(self, duty_cycle_a):
        self.led_a.set_pwm(self.f_pwm, duty_cycle_a)

    def set_pwm_b(self, duty_cycle_b):
        self.led_b.set_pwm(self.f_pwm, duty_cycle_b)

    def close(self):
        """Cleanup GPIO and stop PWM."""
        try:
            # Stop PWM
            self.led_a.stop()
            self.led_b.stop()
        finally:
            # Cleanup GPIO
            GPIO.cleanup([self.pin_a, self.pin_b])

    # Method for printing the info GPIO.RPI_INFO
    def print_info(self):
        print("LED Pin A:", self.pin_a)
        print("LED Pin B:", self.pin_b)
        print("PWM Frequency:", self.f_pwm)