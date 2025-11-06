# Raspberry Pi

## Initialisierung

## 

### 🛠️ Service-Datei anlegen (floorlight.service)

Mit einer Service-Datei kannst du dein Python-Skript automatisch beim Systemstart ausführen lassen.

---

#### 1️⃣ Service-Datei erstellen

Öffne auf dem Raspberry Pi ein Terminal und tippe:

```bash
sudo nano /etc/systemd/system/floorlight.service
```

---

#### 2️⃣ Inhalt einfügen 


```ini
[Unit]
Description=Floorlight PWM Script
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/oliver/pi/floorlight/python/src/main.py
WorkingDirectory=/home/oliver/pi/floorlight/python/src
StandardOutput=inherit
StandardError=inherit
Restart=always
User=oliver
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```


---

#### 3️⃣ Service aktivieren und starten

```bash
sudo systemctl daemon-reload
sudo systemctl enable floorlight.service
sudo systemctl start floorlight.service
```

---

#### 4️⃣ Status prüfen

```bash
sudo systemctl status floorlight.service
```

Du solltest sehen, dass dein Skript läuft.  
Falls Fehler auftreten, kannst du die Log-Ausgabe live mitverfolgen:

```bash
journalctl -u floorlight.service -f
```

---

#### 5️⃣ Optional: Service stoppen oder deaktivieren

```bash
sudo systemctl stop floorlight.service
sudo systemctl disable floorlight.service
```

---

💡 **Tipp:**  
Wenn du Änderungen an der Service-Datei machst, vergiss nicht, den Daemon neu zu laden:
```bash
sudo systemctl daemon-reload
```

# VS Code
VS Code: Remote-SSH verbinden

# Inbetriebnahme des GY-302 (BH1750) Lichtsensors am Raspberry Pi

Der digitale Lichtsensor **BH1750** auf dem Modul **GY-302** misst die Beleuchtungsstärke in **Lux** und kommuniziert über den **I²C-Bus**. Diese Anleitung beschreibt den Anschluss, die Einrichtung und die Nutzung des Sensors auf einem Raspberry Pi-System.

---

## 1. Hardwareanschluss

Der Sensor arbeitet mit einer Versorgungsspannung von **3,3 V** und darf **nicht** an 5 V angeschlossen werden.  
Die Verbindung erfolgt über die I²C-Pins des Raspberry Pi.

| GY-302 (BH1750) | Raspberry Pi GPIO-Pin | Beschreibung |
|------------------|------------------------|---------------|
| **VCC** | Pin 1 (3.3 V) | Versorgung |
| **GND** | Pin 6 (GND) | Masse |
| **SCL** | Pin 5 (GPIO 3 / SCL) | I²C-Taktleitung |
| **SDA** | Pin 3 (GPIO 2 / SDA) | I²C-Datenleitung |

---

## 2. I²C-Schnittstelle aktivieren

Die I²C-Schnittstelle wird über das Konfigurationstool des Raspberry Pi aktiviert:

```bash
sudo raspi-config
```

- Menüpfad: **Interface Options → I2C → Enable → Yes**  
- Anschließend Neustart:

```bash
sudo reboot
```

---

## 3. Sensorerkennung prüfen

Nach dem Neustart kann überprüft werden, ob der Sensor erkannt wird:

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
```

Wird der Sensor korrekt erkannt, erscheint in der Ausgabe typischerweise die Adresse **0x23** oder **0x5C**.

Beispielausgabe:

```
     0 1 2 3 4 5 6 7 8 9 a b c d e f
00:          -- -- -- -- -- -- -- --
10: -- -- -- 23 -- -- -- -- -- -- -- --
```

---


---

## 5. Beispielskript in Python

Das folgende Beispielskript liest fortlaufend den Lux-Wert aus und gibt ihn in der Konsole aus.

```python
#!/usr/bin/env python3
import time
import smbus
import bh1750

bus = smbus.SMBus(1)
sensor = bh1750.BH1750(bus)

while True:
    lux = sensor.measure_high_res()
    print(f"Helligkeit: {lux:.2f} lx")
    time.sleep(1)
```

Das Skript kann unter dem Namen `bh1750_test.py` gespeichert und mit folgendem Befehl gestartet werden:

```bash
python3 bh1750_test.py
```

---

## 6. Typische Beleuchtungsstärken

| Umgebung | Typischer Messwert |
|-----------|--------------------|
| Mondlicht | ca. 0,1 lx |
| Dämmerung | 10 – 100 lx |
| Innenraum (Büro) | 300 – 500 lx |
| Tageslicht (Sonne) | > 10 000 lx |

---

## 7. Fehlerbehebung

| Problem | Mögliche Ursache | Lösung |
|----------|------------------|--------|
| Sensor wird nicht erkannt | Falsche Verkabelung | SDA/SCL, VCC und GND prüfen |
| Keine Ausgabe im Python-Skript | Falsche I²C-Adresse | Adresse 0x5C statt 0x23 testen |
| Mehrere I²C-Geräte vorhanden | Adresskonflikt | I²C-Adresse im Code anpassen |

---

## 8. Weiterführende Nutzung

Der Sensor kann auch zur **Datenprotokollierung** oder für **Hausautomationssysteme** verwendet werden, etwa durch die Weitergabe der Messwerte an:

- CSV-Dateien (Langzeitprotokollierung)
- MQTT-Broker (z. B. Home Assistant)
- Web- oder Cloud-Dienste
