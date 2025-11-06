# src/bh1750.py
# Minimal driver for the BH1750 light sensor on Raspberry Pi via I2C.
import time
import smbus
from pathlib import Path
import utils


# Addresses depending on ADD pin:
ADDR_LOW  = 0x23
ADDR_HIGH = 0x5C

# Commands/modes (datasheet)
POWER_DOWN   = 0x00
POWER_ON     = 0x01
RESET        = 0x07  # nur gültig wenn powered on

# Sample modes for BH1750
CONTINUOUS_HIRES_MODE   = 0x10  # 
CONTINUOUS_HIRES_MODE_2 = 0x11  # 
CONTINUOUS_LORES_MODE   = 0x13  # 

ONE_TIME_HIRES_1  = 0x20
ONE_TIME_HIRES_2  = 0x21
ONE_TIME_LORES    = 0x23

class BH1750:
    """Class for interfacing with the BH1750 light sensor via I2C."""
    def __init__(self, addr=ADDR_LOW, mode=CONTINUOUS_HIRES_MODE):
        """
        Constructor: Initialize the BH1750 sensor.
        """
        self.addr = addr
        self.bus  = smbus.SMBus(1)
        self.mode = mode
        self._write(POWER_ON)
        time.sleep(0.02)
        self.set_mode(mode)

    def _write(self, byte):
        """
        Write a byte to the sensor.
        """
        self.bus.write_byte(self.addr, byte)

    def power_down(self):
        """
        Power down the sensor.
        """
        self._write(POWER_DOWN)

    def reset(self):
        """
        Reset the sensor (must be powered on).
        """
        self._write(RESET)

    def set_mode(self, mode):
        """
        Set the operating mode of the sensor.
        """
        self.mode = mode
        self._write(mode)

    def read_lux(self):
        """
        Read light level in lux.
        """
        # Wait time depending on mode (rough wait time)
        if self.mode in (CONTINUOUS_HIRES_MODE, CONTINUOUS_HIRES_MODE_2, ONE_TIME_HIRES_1, ONE_TIME_HIRES_2):
            time.sleep(0.18)   # ~180 ms
        else:
            time.sleep(0.024)  # ~24 ms

        # Read 2 bytes and convert to lux. Factor from datasheet ~1.2.
        # For CONT_* modes, setting mode once in __init__ is sufficient.
        data = self.bus.read_i2c_block_data(self.addr, self.mode)
        raw = (data[0] << 8) | data[1]
        lux = raw / 1.2
        return lux
