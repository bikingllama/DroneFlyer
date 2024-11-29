import spidev
import time
import RPi.GPIO as GPIO
import numpy as np

GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.OUT, initial=GPIO.HIGH)

# MCP4261 Registers
VOL0_ADDR = 0x00  # Wiper 0
VOL1_ADDR = 0x10  # Wiper 1
CMD_WRITE = 0x00  # Command to write data

# SPI Setup
spi = spidev.SpiDev()  # Create SPI object
spi.open(0, 0)         # Open SPI bus 0, device 0 (CE0)
spi.max_speed_hz = 10**7  # Set SPI speed (50 kHz is a good start)

# Define stick CS's
CSL = 31
CSR = 29

def set_wiper(address, value):
    """
    Set the wiper position of the MCP4261.
    address: 8-bit address of the potentiometer.
    value: 8-bit wiper position (0-255).
    """
    cmd = CMD_WRITE | address  # Combine command and address
    print("First byte is {:08b} & second byte is {:08b}".format(cmd, value))
    GPIO.output(31, GPIO.LOW)
    spi.xfer2([cmd, value])    # Send 2-byte SPI command
    GPIO.output(31, GPIO.HIGH)
    print(f"Set wiper {address} to {value}")

def UpdateResistance(VnV, Stick, Axis, Value):
    InitB = 0x8000
    CommandB = 0x00

    if Axis == 0:
        AxisB = 0x00
    elif Axis == 1:
        AxisB = 0x1000

    if VnV == 0:
        VnVB = 0x00
    elif VnV == 1:
        VnVB = 0x2000

    # Convert value to integer to set pot to
    N = int(np.floor((Value - 75) * 256 / 10000))

    # Check if N is within range (0-256)
    if N > 256 or N < 0:
        print(f"Error! Value for resistance is out of range at N = {N}")
        N = min(max(N, 0), 256)

    # Assemble byte
    Byte = InitB | CommandB | AxisB | VnVB | N
    Byte = Byte & 0x7EFF

    # Split byte into two 8-bit values
    Byte1 = (Byte >> 8) & 0xFF  # Most significant 8 bits
    Byte2 = Byte & 0xFF         # Least significant 8 bits

    # Call the function to set the wiper with two separate bytes
    set_wiper(Byte1, Byte2)

Val = 0
UpdateResistance(0, 0, 0, 0)
time.sleep(1)
