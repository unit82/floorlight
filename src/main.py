#!/usr/bin/env python3
from __future__ import annotations
import time
import RPi.GPIO as GPIO

PWM_PIN = 12        # GPIO 12 (Pin 32)
FREQUENCY = 3000    # 3 kHz

def main() -> int:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PWM_PIN, GPIO.OUT)

    pwm = GPIO.PWM(PWM_PIN, FREQUENCY)
    pwm.start(0)

    RampTime = 4     # Sekunden für Auf- oder Abwärtsrampe
    steps = 100      # Anzahl Schritte
    delay = RampTime / steps

    print(f"Starte Rampenlauf: {RampTime}s auf / {RampTime}s ab, {steps} Schritte, {delay:.4f}s pro Schritt.")

    try:
        # Aufwärtsrampe
        for i in range(steps + 1):
            duty = i * 100 / steps
            pwm.ChangeDutyCycle(duty)
            time.sleep(delay)

        time.sleep(2)

        # Abwärtsrampe
        for i in range(steps, -1, -1):
            duty = i * 100 / steps
            pwm.ChangeDutyCycle(duty)
            time.sleep(delay)

        time.sleep(2)

    except KeyboardInterrupt:
        print("Beendet durch Benutzer.")
    finally:
        pwm.stop()
        GPIO.cleanup()
        print("GPIO aufgeräumt, PWM gestoppt.")
    return 0

if __name__ == "__main__":
    main()
