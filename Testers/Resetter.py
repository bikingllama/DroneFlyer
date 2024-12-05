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



def WriteByte(CurrCS, Byte1, Byte2):
	print("Sending {} and {}".format(Byte1, Byte2))
	GPIO.output(CurrCS, GPIO.LOW)
	Response = spi.xfer2([Byte1, Byte2])    # Send 2-byte SPI command
	GPIO.output(CurrCS, GPIO.HIGH)
	time.sleep(0.01)
	print(Response)
		
    

N = 145
WriteByte(CSL, 0b00000000, N)
WriteByte(CSL, 0b00010000, N)
WriteByte(CSR, 0b00000000, N)
WriteByte(CSR, 0b00010000, N)
