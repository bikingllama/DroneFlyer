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

 
def UpdateResistance(VnV, Stick, Axis, Value):
	# Initializes double byte
	InitB = 0x8000
	
	# Defines that it needs to write
	CommandB = 0x00

	# Defines which pot to write to
	if Axis == 0:
		AxisB = 0x00
	elif Axis == 1:
		AxisB = 0x1000

	# Defines whether to write to volatile or nonvolatile
	if VnV == 0:
		VnVB = 0x00
	elif VnV == 1:
		VnVB = 0x2000

    # Converts value to integer to set pot to. Arbitratily rounded down
    # R_WB = R_AB*N/256+RW
    # N = (R_WB-RW)*256/R_AB
	N = int(np.floor((Value-75)*256/10000))

    # Checks if value for N is within range (0-256)
	if (N > 256 or N < 0):
		print("Error! Value for resistance is out of range at N = " + str(N))
		if N > 256:
			N = 256
		if N < 0:
			N = 0

    # Assembles byte
	Byte = InitB | CommandB | AxisB | VnVB | N

    # Sets bit 16 and 9 to zero
	Byte = Byte & 0x7EFF
    
    # Splits byte into two eights
	Byte1 = Byte >> 8
	Byte2 = Byte & 0b11111111

	if not Stick:
		CurrOutPin = CSL
	else:
		CurrOutPin = CSR
        
    # Initialize response
	Response = 0b1
    

    #Sends output
	set_wiper(Byte1,Byte2)
 
 
def set_wiper(address, value):
	address = int(address)
	value = int(value)
	
	"""
    Set the wiper position of the MCP4261.
    address: 4-bit address of the potentiometer.
    value: 8-bit wiper position (0-255).
    """
	cmd = CMD_WRITE | address  # Combine command and address
	print("First byte is {:08b} & second byte is {:08b}".format(cmd, value))
	GPIO.output(31, GPIO.LOW)
	spi.xfer2([cmd, value])    # Send 2-byte SPI command
	GPIO.output(31, GPIO.HIGH)
	print(f"Set wiper {address} to {value}")
 

Val = 0

UpdateResistance(0,0,0,0)
time.sleep(1)

#UpdateResistance(0,0,0,5000)
time.sleep(1)
