# Floorlight

Kleines Python-Projekt zur Ansteuerung von LED-/Bodenbeleuchtung auf einem Raspberry Pi.

Kurzbeschreibung
- Steuerung per PWM über GPIO (siehe `src/main.py`).
- Hardware: MOSFET/Transistor für LED-Strips, externe Stromversorgung, gemeinsamer GND mit dem Pi.

Quickstart
1. Ins Projektverzeichnis wechseln:
```powershell
cd \\\192.168.178.39\pi\floorlight\python
```
2. Abhängigkeiten installieren (falls nötig):
```powershell
sudo apt update; sudo apt install -y python3 python3-pip
pip3 install -r requirements.txt
```
3. Script als Root starten (GPIO-Zugriff):
```powershell
sudo python3 -m src
```

Wichtige Hinweise
- GPIO liefert nur sehr wenig Strom. Verwende einen MOSFET oder Treiber für LED-Strips.
- Achte auf gemeinsame Masse (Pi GND mit LED-Versorgung verbinden).
- Wenn du WS2812/Neopixel-LEDs verwendest, benötigst du eine spezielle Bibliothek (z. B. rpi_ws281x / adafruit-circuitpython-neopixel) — RPi.GPIO ist dafür nicht geeignet.

Weitere Dokumentation: siehe `docs/`.

Kontribution
- `CONTRIBUTING.md` ist optional; pull requests und Issues sind willkommen.

License
- Falls noch nicht gesetzt: füge eine `LICENSE`-Datei im Projekt-Root hinzu.
