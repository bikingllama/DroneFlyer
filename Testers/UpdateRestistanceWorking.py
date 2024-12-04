import RPi.GPIO as GPIO
import spidev
import numpy as np
import time

# GPIO setup
GPIO.setmode(GPIO.BOARD)  # Use board pins instead of the GPI index


CSL = 31
CSR = 29

GPIO.setup(CSL, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(CSR, GPIO.OUT, initial = GPIO.HIGH)

# SPI setup
# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 10**6


Rmin = 92
Rmax = 8030
RW = 91
RAB = 8150



# This function updates the value for one of the resistors.
# VnV determines if it writes to volatile or nonvolatile memory, 0 is volatile.
# The stick defines if its the left or right stick, 0 is left, 1 is right.
# The axis defines whether is up/down or sideways, 0 is horizontal, 1 is vertical.


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
    N = int(np.floor((Value-RW)*256/RAB))

    # Checks if value for N is within range (0-256)
    if (N > 255 or N < 0):
        print("Error! Value for resistance is out of range at N = " + str(N))
        if N > 255:
            N = 255
        elif N < 0:
            N = 0
            
    # Assures that N is within range
    N = N & 0b111111111

    # Assembles byte
    Byte = InitB | CommandB | AxisB | VnVB | N
    
    # Sets bit 16 to zero
    Byte = Byte & 0x7FFF
    
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
    try:
        print("Bytes are {} & {}".format(Byte1, Byte2))
        print("First byte is {:08b} & second byte is {:08b}".format(Byte1, Byte2))
        GPIO.output(CurrOutPin, GPIO.LOW)
        Response = spi.xfer2([Byte1, Byte2])    # Send 2-byte SPI command
        GPIO.output(CurrOutPin, GPIO.HIGH)
        time.sleep(0.01)
	
    except Exception as Excp:
        print("Exception when sending:\n")
        print(Excp)

        
    # Prints response
    if Response != 0b1:
        print("Recieved response:\n")
        print(Response)

    # Sets both CS-pins to be high to be sure
    GPIO.output(CSL, GPIO.HIGH)
    GPIO.output(CSR, GPIO.HIGH)

    print("Updated digipot {} wiper {} to value N= {}, for potentionemter".format(Stick+1,Axis,N))
    
    time.sleep(0.1)
    

UpdateResistance(0, 0, 0, 2000)




