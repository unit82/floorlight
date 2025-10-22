#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, math


class LedSoftPwmGPIO:
    """Class for controlling an LED via software PWM on two GPIO pins.
    Uses dithering to achieve smooth brightness levels with gamma correction."""
    def __init__(self, pin, f_pwm=2000, gamma=1.2):
        self.pin = pin
        self.f_pwm = f_pwm           # 2 kHz is a good default
        self.Tpwm  = 1.0 / f_pwm # PWM period in seconds
        self.gamma = gamma
        # GPIO setup
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # Pin setup
        GPIO.setup(self.pin, GPIO.OUT)
        # PWM setup
        self.pwm = GPIO.PWM(self.pin, self.f_pwm)
        self.pwm.start(0.0)

    def _apply_percent(self, pct):
        """Set the duty cycle (0..100)."""
        if pct < 0: pct = 0
        if pct > 100: pct = 100
        self.pwm.ChangeDutyCycle(pct)

    def _set_level_dithered(self, level01, window=100):
        """Return the PWM duty cycle for a given brightness level (0.0..1.0),"""
        x = 0.0 if level01 < 0 else (1.0 if level01 > 1 else float(level01))
        y = x ** self.gamma                     # Gamma correction
        target_pct = 100.0 * y                  # 0..100
        lo = int(math.floor(target_pct))
        hi = min(100, lo + 1)
        frac = target_pct - lo                  # Fraction for 'hi'
        err = 0.0
        hi_left = int(round(frac * window))     # how often 'hi' appears in this window

        # Equal distribution of 'hi' and 'lo' over the window
        for _ in range(window):
            err += frac
            if err >= 1.0 and hi_left > 0:
                self._apply_percent(hi)
                err -= 1.0
                hi_left -= 1
            else:
                self._apply_percent(lo)
            time.sleep(self.Tpwm)

    def ramp(self, duration_s=5.0, start_level=0.0, end_level=1.0, updates=100, dither_window=10):
        """
        Soft ramp between two brightness levels over a given duration.
        Uses a cosine S-curve for smooth transitions.
        - duration_s: Total duration
        - updates: Number of target values (averaged over 'dither_window' periods)
        - dither_window: Periods per update (80 → ~80 ms at 1 kHz)
        """
        steps = max(1, int(updates))
        for k in range(steps + 1):
            u = k / steps
            s = 0.5 - 0.5 * math.cos(math.pi * u)  # S-curve
            level = start_level + (end_level - start_level) * s
            self._set_level_dithered(level, window=dither_window)

    def set_level(self, level01, settle_ms=80):
        """Directly set brightness (briefly dithered to smooth 1% steps)."""
        window = max(1, int(self.f_pwm * (settle_ms/1000.0)))
        self._set_level_dithered(level01, window=window)

    def off(self):
        """Turn off the LED."""
        self._apply_percent(0)

    def close(self):
        """Cleanup GPIO and stop PWM."""
        try:
            # Stop PWM
            self.off()
            self.pwm.stop()
        finally:
            # Cleanup GPIO
            GPIO.cleanup([self.pin])
