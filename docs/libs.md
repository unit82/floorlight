# Third-party libraries / External docs

Kurze Liste der externen Bibliotheken, die im Projekt verwendet werden.

## RPi.GPIO
- Zweck: GPIO-Zugriff und PWM (Basis).
- Install: `sudo apt install python3-rpi.gpio`
- Docs: https://pypi.org/project/RPi.GPIO/ / https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/
- Hinweis: Erfordert meist `sudo` für direkten GPIO-Zugriff.

## gpiozero
- Zweck: High-level GPIO-API, MotionSensor, PWMLED, etc.
- Install: `pip3 install gpiozero`
- Docs: https://gpiozero.readthedocs.io/
- Hinweis: Eignet sich gut für Event-Callbacks und Test-Mocks.

## pigpio / rpi_ws281x (falls WS2812 used)
- Zweck: präzise PWM/Timing für adressierbare LEDs.
- Install/Daemon: `sudo apt install pigpio` + `sudo systemctl enable --now pigpiod`
- Docs: https://abyz.me.uk/rpi/pigpio/ and https://github.com/jgarff/rpi_ws281x

## i2c-tools
- Zweck: I²C-Diagnose-Tools (i2cdetect, i2cget)
- Install: `sudo apt install i2c-tools`
- Docs: https://linux.die.net/man/1/i2cdetect
