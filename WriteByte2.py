



import spidev
import numpy as np
import RPi.GPIO as GPIO
import time

# Define stick CS's
CSL = 31
CSR = 29

# Set CS as output and initilazise
GPIO.setmode(GPIO.BOARD)
GPIO.setup(CSL, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(CSR, GPIO.OUT, initial=GPIO.HIGH)

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 10**6



def WriteByte(Byte):
	Num = 2500
	print("Sending {}".format(Byte))
	GPIO.output(31, GPIO.LOW)
	Response = spi.xfer2([Byte])    # Send 2-byte SPI command
	print("Is {:016b}".format(Byte))
	GPIO.output(31, GPIO.HIGH)
	time.sleep(0.01)
	print(Response)
	
	#Response2 = spi.xfer2([0b0000110000000000])
	#print("Response 2 {}".format(Response2))
    
    
WriteByte(0b0000000011111111)
#WriteByte(0x0000001111100001)
time.sleep(3)
WriteByte(0b00000000000000000)
