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
import time, math
import pigpio

######################################################################################################
# Constants
######################################################################################################

DUTY_MIN          = 0.0
DUTY_MAX          = 100.0
N_DUTY_MAX        = 101
N_X               = 1
X_DUTY            = N_X * N_DUTY_MAX
N_DUTY_PIGPIO_MAX = 1000000  # pigpio uses duty cycle from 0 to 1,000,000
DUTY_FACTOR_MAX = N_DUTY_PIGPIO_MAX/100  # pigpio uses duty cycle from 0 to 1,000,000

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
        T_ramp (float): Max ramp time in seconds.
        duty_a (float): Initial duty cycle for LED A (percent).
        duty_b_factor (float): Factor to determine duty cycle for LED B relative to LED A
        f_pwm (float): PWM frequency in Hz.
    """
    def __init__(self, pin_a=12, pin_b=13, T_ramp=2.0, duty_a=0, duty_b_factor=1/2, f_pwm=200):
        
        self.pwm = pigpio.pi()
        if not self.pwm.connected:
            raise RuntimeError("Keine Verbindung zu pigpiod – läuft der Daemon?")

        # Public attributes
        self.pin_a         = pin_a
        self.pin_b         = pin_b
        self.T_ramp    = T_ramp  # Max ramp time in seconds
        self.duty_a        = float(duty_a)  # Initial duty cycle for LED A (percent)
        self.duty_b        = self.duty_a * self._clamp_duty_b_factor(duty_b_factor) 
        self.duty_b_factor = self._clamp_duty_b_factor(duty_b_factor)
        self.f_pwm         = f_pwm  # 200 Hz is a good default

        # Private attributes (Constants)
        self._T_duty = self.T_ramp / (2*N_DUTY_MAX)


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
        x_duty_float = 2*N_DUTY_MAX/n_duty
        x_duty = math.ceil(x_duty_float)
        if b_print:
            print("_N_duty: {}, n_duty: {}, x_duty_float: {}".format(N_DUTY_MAX, n_duty, x_duty_float))
            print("Calculating x_duty = ceil(2*{}/{})) = ceil({}) = {}".format(N_DUTY_MAX, n_duty, x_duty_float, x_duty))
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

        # Downsample to at most X_DUTY elements by picking evenly spaced indices (keep endpoints)
        n = len(vector_duty)
        if n > X_DUTY:
            if X_DUTY <= 1:
                vector_duty = [vector_duty[0]]
            else:
                step = (n - 1) / (X_DUTY - 1)
                indices = [min(n-1, int(round(i * step))) for i in range(X_DUTY)]
                vector_duty = [vector_duty[idx] for idx in indices]
        return vector_duty
    
    def _get_vector_duty_resample(self, x_duty, vector_duty, duty_end):
        """Resample the duty cycle vector to match x_duty steps."""
        # Every element in vector_duty is repeated x_duty times
        vector_duty_resampled = []
        for duty in vector_duty:
            vector_duty_resampled.extend([duty] * x_duty)
        # Trim the resampled vector to not exceed X_DUTY
        vector_duty_resampled_trimmed = vector_duty_resampled[:X_DUTY]
        # Force the last element to be duty_end
        vector_duty_resampled_trimmed[-1] = duty_end
        # Return the resampled vector
        return vector_duty_resampled_trimmed
    
    def _get_vector_duty_resample_fraction(self, vector_duty_resampled_a):
        """Resample the duty cycle vector to match x_duty steps."""
        # Iterate through vector_duty_resampled_a and scale and round up each value by duty_b_factor. 
        # But for vector_duty_resampled_a values 1 and 0, keep them as is.
        vector_duty_resampled_b = []
        for duty in vector_duty_resampled_a:
            if duty == 1:
                vector_duty_resampled_b.append(1)
            elif duty == 0:
                vector_duty_resampled_b.append(0)
            else:
                vector_duty_resampled_b.append(math.ceil(duty * self.duty_b_factor))
        return vector_duty_resampled_b
    
    def _get_vector_duty_resample_ab(self, duty_start, duty_end, b_print=True):
        duty_start_a = duty_start
        duty_end_a   = duty_end
        duty_start_b = duty_start * self.duty_b_factor
        duty_end_b   = duty_end * self.duty_b_factor
        n_duty_a = self._get_n_duty(duty_start_a, duty_end_a)
        n_duty_b = self._get_n_duty(duty_start_b, duty_end_b)
        x_duty_a = self._get_x_duty(n_duty_a, b_print=b_print)
        vector_duty_a = self._get_vector_duty(duty_start_a, duty_end_a)
        vector_duty_b = self._get_vector_duty(duty_start_b, duty_end_b)
        if b_print:
            print("Ramping LED A and B from {}% to {}% over {} seconds: n_duty = {}, x_duty = {}".format(duty_start, duty_end, self.T_ramp, n_duty_a , x_duty_a))
            print("N_duty: {}, n_duty: {}, X_duty: {}, duty_b_factor: {}".format(N_DUTY_MAX, n_duty_a, x_duty_a, self.duty_b_factor))
            print("Duty Vector (length: {}) for ramping LED A: {}".format(len(vector_duty_a), [v / DUTY_FACTOR_MAX for v in vector_duty_a]))
            print("Duty Vector (length: {}) for ramping LED B: {}".format(len(vector_duty_b), [v / DUTY_FACTOR_MAX for v in vector_duty_b]))
        return vector_duty_a, vector_duty_b
    
    def _get_dynamic_T_duty(self, duty_start, duty_end, b_print=True):
        """
        The lower the duty cycle range, the shorter the ramp time in order
        to prevent flickering at low duty cycles.
        """
        n_duty = self._get_n_duty(duty_start, duty_end)
        # Cal. n_duty / N_DUTY_MAX
        rel_n_duty_to_max = n_duty / N_DUTY_MAX
        T_ramp = self.T_ramp * rel_n_duty_to_max
        dynamic_T_duty = T_ramp / (2*N_DUTY_MAX)
        if b_print:
            print("dynamic_T_duty  = self.T_ramp sec * rel_n_duty_to_max / (2*N_DUTY_MAX) = {:.2f} sec * {:.5f} / (2*{}) = {:.5f} sec vs. _T_duty = {:.4f} seconds" \
                .format(self.T_ramp, rel_n_duty_to_max, N_DUTY_MAX, dynamic_T_duty, self._T_duty))
        return dynamic_T_duty

    #########################################################
    # Public Methods
    #########################################################

    def ramp_a(self, duty_start, duty_end, b_print=True):
        """Ramp both LEDs from duty_start to duty_end over T_ramp seconds."""
        n_duty = self._get_n_duty(duty_start, duty_end)
        x_duty = self._get_x_duty(n_duty)
        vector_duty = self._get_vector_duty(duty_start, duty_end)
        vector_duty_resampled = self._get_vector_duty_resample(x_duty, vector_duty, duty_end)
        for duty in vector_duty_resampled:
            self.led_a.set_pwm(self.f_pwm, duty)
            #print("Setting LED A duty to {}%".format(duty))
            time.sleep(self._T_duty)

    def ramp_b(self, duty_start, duty_end, b_print=True):
        """Ramp both LEDs from duty_start to duty_end over T_ramp seconds."""
        n_duty = self._get_n_duty(duty_start, duty_end)
        x_duty = self._get_x_duty(n_duty)
        vector_duty = self._get_vector_duty(duty_start, duty_end)
        vector_duty_resampled = self._get_vector_duty_resample(x_duty, vector_duty, duty_end, b_print=b_print)
        for duty in vector_duty_resampled:
            self.pwm.hardware_PWM(self.pin_b, self.f_pwm, duty)
            time.sleep(self._T_duty)
    

    def ramp_ab(self, duty_start, duty_end, b_print=True):
        """Ramp both LEDs from duty_start to duty_end over T_ramp seconds."""
        vector_duty_resampled_a, vector_duty_resampled_b = self._get_vector_duty_resample_ab(duty_start*DUTY_FACTOR_MAX, duty_end*DUTY_FACTOR_MAX, b_print=b_print)
        for i in range(len(vector_duty_resampled_a)):
            duty_a = vector_duty_resampled_a[i]
            duty_b = vector_duty_resampled_b[i]
            self.pwm.hardware_PWM(self.pin_a, self.f_pwm, duty_a)
            self.pwm.hardware_PWM(self.pin_b, self.f_pwm, duty_b)
            time.sleep(self._T_duty)

    def set_pwm_a(self, duty_cycle_a):
        self.pwm.hardware_PWM(self.pin_a, self.f_pwm, duty_cycle_a*N_DUTY_PIGPIO_MAX)

    def set_pwm_b(self, duty_cycle_b):
        self.pwm.hardware_PWM(self.pin_b, self.f_pwm, duty_cycle_b*N_DUTY_PIGPIO_MAX)

    def close(self):
        """Cleanup GPIO and stop PWM."""
        try:
            # Stop PWM
            self.pwm.hardware_PWM(self.pin_a, 0, 0)
            self.pwm.hardware_PWM(self.pin_b, 0, 0)
            self.pwm.stop()
        finally:
            # Cleanup GPIO
            self.pwm.stop()


    # Method for printing the info GPIO.RPI_INFO
    def print_info(self):
        print("LED Pin A:", self.pin_a)
        print("LED Pin B:", self.pin_b)
        print("PWM Frequency:", self.f_pwm)