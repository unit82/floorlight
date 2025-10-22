#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time, math


class LedSoftPwmGPIO:
    def __init__(self, pin0=12, pin1=13, f_pwm=2000, gamma=1.2):
        self.pin0  = pin0
        self.pin1  = pin1
        self.f_pwm = f_pwm           # 2 kHz ist ein guter Kompromiss
        self.Tpwm  = 1.0 / f_pwm
        self.gamma = gamma
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin0, GPIO.OUT)
        GPIO.setup(self.pin1, GPIO.OUT)
        self.pwm0 = GPIO.PWM(self.pin0, self.f_pwm)
        self.pwm1 = GPIO.PWM(self.pin1, self.f_pwm)
        self.pwm0.start(0.0)
        self.pwm1.start(0.0)

    def _apply_percent(self, pct0, pct1=0):
        if pct0 < 0: pct0 = 0
        if pct0> 100: pct0= 100
        if pct1 < 0: pct1 = 0
        if pct1> 100: pct1= 100
        self.pwm0.ChangeDutyCycle(pct0)
        self.pwm1.ChangeDutyCycle(pct1)

    def _set_level_dithered(self, level01, window=100):
        """Gibt 'level01' (0..1) über 'window' PWM-Perioden dithered aus."""
        x = 0.0 if level01 < 0 else (1.0 if level01 > 1 else float(level01))
        y = x ** self.gamma                     # Gamma-Korrektur
        target_pct = 100.0 * y                  # 0..100
        lo = int(math.floor(target_pct))
        hi = min(100, lo + 1)
        frac = target_pct - lo                  # Anteil für 'hi'
        err = 0.0
        hi_left = int(round(frac * window))     # wie oft 'hi' in diesem Fenster

        # gleichmäßige Verteilung über das Fenster
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
        Weiche Rampe:
        - duration_s: Gesamtdauer
        - updates: Anzahl Zielwerte (jeweils über 'dither_window' Perioden gemittelt)
        - dither_window: Perioden pro Update (80 → ~80 ms bei 1 kHz)
        """
        steps = max(1, int(updates))
        for k in range(steps + 1):
            u = k / steps
            s = 0.5 - 0.5 * math.cos(math.pi * u)  # S-Kurve
            level = start_level + (end_level - start_level) * s
            self._set_level_dithered(level, window=dither_window)

    def set_level(self, level01, settle_ms=80):
        """Direkt auf Helligkeit fahren (kurz gedithered, um die 1%-Stufen zu glätten)."""
        window = max(1, int(self.f_pwm * (settle_ms/1000.0)))
        self._set_level_dithered(level01, window=window)

    def off(self):
        self._apply_percent(0)

    def close(self):
        try:
            self.off()
            self.pwm0.stop()
            self.pwm1.stop()
        finally:
            GPIO.cleanup(self.pin)
