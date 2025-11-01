# Raspberry Pi

## Initialisierung

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