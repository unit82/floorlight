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


class LedPairSoftPwm:
    """Control two LEDs (two GPIO pins) with coordinated soft PWM ramps.

    This class implements a dithered PWM approach similar to
    LedSoftPwmGPIO but applies updates to both channels inside the
    same timing loop so changes occur quasi-gleichzeitig.
    """
    def __init__(self, pin_a=12, pin_b=13, f_pwm=2000, gamma=1.2):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.f_pwm = f_pwm
        self.Tpwm = 1.0 / f_pwm
        self.gamma = gamma

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.pin_a, GPIO.OUT)
        GPIO.setup(self.pin_b, GPIO.OUT)

        self.pwm_a = GPIO.PWM(self.pin_a, self.f_pwm)
        self.pwm_b = GPIO.PWM(self.pin_b, self.f_pwm)
        self.pwm_a.start(0.0)
        self.pwm_b.start(0.0)

    def _apply_percent_both(self, pct_a, pct_b):
        """Apply immediate duty-cycle values (0..100) to both channels."""
        if pct_a < 0: pct_a = 0
        if pct_a > 100: pct_a = 100
        if pct_b < 0: pct_b = 0
        if pct_b > 100: pct_b = 100
        self.pwm_a.ChangeDutyCycle(pct_a)
        self.pwm_b.ChangeDutyCycle(pct_b)

    def _set_levels_dithered(self, level_a, level_b, window=100):
        """Dither both channels together over `window` PWM periods.

        level_a/level_b are in 0.0..1.0 range.
        """
        def clamp01(x):
            if x <= 0.0: return 0.0
            if x >= 1.0: return 1.0
            return float(x)

        a = clamp01(level_a)
        b = clamp01(level_b)
        ta = (a ** self.gamma) * 100.0
        tb = (b ** self.gamma) * 100.0

        lo_a = int(math.floor(ta))
        hi_a = min(100, lo_a + 1)
        frac_a = ta - lo_a
        hi_left_a = int(round(frac_a * window))

        lo_b = int(math.floor(tb))
        hi_b = min(100, lo_b + 1)
        frac_b = tb - lo_b
        hi_left_b = int(round(frac_b * window))

        err_a = 0.0
        err_b = 0.0

        for _ in range(max(1, int(window))):
            err_a += frac_a
            if err_a >= 1.0 and hi_left_a > 0:
                out_a = hi_a
                err_a -= 1.0
                hi_left_a -= 1
            else:
                out_a = lo_a

            err_b += frac_b
            if err_b >= 1.0 and hi_left_b > 0:
                out_b = hi_b
                err_b -= 1.0
                hi_left_b -= 1
            else:
                out_b = lo_b

            # apply both outputs in the same loop iteration -> near-simultaneous
            self._apply_percent_both(out_a, out_b)
            time.sleep(self.Tpwm)

    def ramp_both(self, duration_s=5.0,
                  start_a=0.0, end_a=1.0,
                  start_b=0.0, end_b=1.0,
                  updates=100, dither_window=10):
        """Ramp both channels concurrently using the same S-curve timing.

        start_a/end_a and start_b/end_b are brightness in 0.0..1.0.
        """
        steps = max(1, int(updates))
        for k in range(steps + 1):
            u = k / steps
            s = 0.5 - 0.5 * math.cos(math.pi * u)
            level_a = start_a + (end_a - start_a) * s
            level_b = start_b + (end_b - start_b) * s
            self._set_levels_dithered(level_a, level_b, window=dither_window)

    def set_levels(self, level_a, level_b, settle_ms=80):
        """Immediately set both brightness levels (brief dither to smooth)."""
        window = max(1, int(self.f_pwm * (settle_ms/1000.0)))
        self._set_levels_dithered(level_a, level_b, window=window)

    def off(self):
        self._apply_percent_both(0, 0)

    def close(self):
        try:
            self.off()
            self.pwm_a.stop()
            self.pwm_b.stop()
        finally:
            GPIO.cleanup([self.pin_a, self.pin_b])
