import spidev
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.OUT, initial=GPIO.HIGH)
 
# MCP4261 Registers
VOL0_ADDR = 0x00  # Wiper 0
VOL1_ADDR = 0x10  # Wiper 1
CMD_WRITE = 0x00  # Command to write data
 
# SPI Setup
spi = spidev.SpiDev()  # Create SPI object
spi.open(0, 0)         # Open SPI bus 0, device 0 (CE0)
spi.max_speed_hz = 50000  # Set SPI speed (50 kHz is a good start)
 
def set_wiper(address, value):
    """
    Set the wiper position of the MCP4261.
    address: 4-bit address of the potentiometer.
    value: 8-bit wiper position (0-255).
    """
    cmd = CMD_WRITE | address  # Combine command and address
    GPIO.output(31,GPIO.LOW)
    spi.xfer2([cmd, value])    # Send 2-byte SPI command
    GPIO.output(31,GPIO.HIGH)
    print(f"Set wiper {address} to {value}")
 
# Main loop
try:
    set_wiper(VOL0_ADDR, 128)  # Set POT0 to mid-scale
    time.sleep(1)
 
    set_wiper(VOL1_ADDR, 64)   # Set POT1 to a lower resistance
    time.sleep(1)
 
except KeyboardInterrupt:
    spi.close()  # Clean up SPI connection
    print("Exiting...")
