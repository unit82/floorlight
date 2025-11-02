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
2. Abhängigkeiten installieren (System + Python):
```bash
# aus dem Projekt-Root
./scripts/install-deps.sh
```
3. Script als Root starten (GPIO-Zugriff):
```powershell
sudo python3 -m src
```

Wichtige Hinweise
- GPIO liefert nur sehr wenig Strom. Verwende einen MOSFET (IRLZ44NPBF) oder Treiber für LED-Strips.
- Achte auf gemeinsame Masse (Pi GND mit LED-Versorgung verbinden).


Systemabhängigkeiten
- Einige Abhängigkeiten müssen systemweit per apt installiert werden, z. B. `i2c-tools`.
- Systempakete sind in `config/apt-requirements.txt` gelistet. Das `scripts/install-deps.sh` Script aktualisiert apt, installiert diese Pakete und danach die Python-Abhängigkeiten aus `requirements.txt`.

Weitere Dokumentation: siehe `docs/`.

Kontribution
- `CONTRIBUTING.md` ist optional; pull requests und Issues sind willkommen.

License
- Falls noch nicht gesetzt: füge eine `LICENSE`-Datei im Projekt-Root hinzu.

