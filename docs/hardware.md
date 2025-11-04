# Hardware / Wiring

Wichtige Hinweise zur sicheren und funktionierenden Verkabelung der Bodenbeleuchtung.

1) Pin-Nummerierung
- In `src/main.py` wird `PWM_PIN = 12` verwendet — das ist BCM 12 (physischer Pin 32 auf dem 40‑Pin Header).

2) Versorgung
- LEDs/LED-Strips müssen von einer geeigneten externen Stromversorgung (z. B. 5V oder 12V) versorgt werden.
- Der Raspberry Pi darf nicht direkt die Last der LEDs treiben.
- Verbinde die Masse der externen Versorgung mit dem Raspberry Pi GND (gemeinsame Masse).

3) Schaltstufe
- Verwende einen logic‑level MOSFET (z. B. IRLZ44N, IRLZ34 oder bessere moderne Typen) oder einen N‑channel MOSFET mit passendem Gate‑Widerstand und Pull‑Down.
- Gate des MOSFET an den PWM‑GPIO (z. B. BCM12), Drain an den negativen Pol des LED‑Strips, Source an GND.
- Füge ggf. eine Freilaufdiode/TVS hinzu, wenn du induktive Lasten schaltest.

4) Software / PWM
- RPi.GPIO bietet softwarebasiertes PWM. Für einfache Helligkeitsregelung ist das meistens ausreichend.
- Für hochfrequente oder zeitkritische Signale (bspw. bestimmte LED‑Protokolle) benötigst du spezielle Treiber/Libraries.

5) Troubleshooting (kurz)
- Stelle sicher, dass du das Script mit root-Rechten startest (`sudo python3 -m src`).
- Prüfe, ob der Pin korrekt verdrahtet ist (BCM vs. physisch!).
- Messe mit Multimeter, ob Gate/Pin Spannung anliegt, wenn PWM läuft.
- Achte auf gemeinsame Masse zwischen Pi und LED‑Versorgung.

6) Hinweis für adressierbare LEDs (WS2812 / Neopixel)
- WS2812 benötigen exakt getaktete Daten; verwende hierfür die passende Bibliothek (rpi_ws281x, adafruit_neopixel) — diese sind nicht kompatibel mit RPi.GPIO PWM.

7) Hardware-Lliste
- Raspberry Pi Zero 2 WH 1GHZ 512MB WLAN
- TRANSISTOR HEXFET IRLZ44NPBF
- GY-302 (BH1750) Lichtsensormodul 
- SEN-HC-SR501 Bewegungssensormodul
- LED-Streifen 5025 3000K-6000K